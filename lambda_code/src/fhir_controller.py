import json
import os
import re
import uuid
from typing import Optional

import boto3
from botocore.config import Config

from cache import Cache
from fhir_repository import ImmunizationRepository, create_table
from fhir_service import FhirService, UpdateOutcome
from models.errors import Severity, Code, create_operation_outcome, ResourceNotFoundError, UnhandledResponseError, \
    ValidationError
from pds_service import PdsService, Authenticator


def make_controller(pds_env: str = os.getenv("PDS_ENV", "int")):
    imms_repo = ImmunizationRepository(create_table())
    boto_config = Config(region_name='eu-west-2')
    cache = Cache(directory="/tmp")
    authenticator = Authenticator(boto3.client('secretsmanager', config=boto_config), pds_env, cache)
    pds_service = PdsService(authenticator, pds_env)

    service = FhirService(imms_repo=imms_repo, pds_service=pds_service)

    return FhirController(fhir_service=service)


def get_service_url(service_env: str = os.getenv("IMMUNIZATION_ENV"),
                    service_base_path: str = os.getenv("IMMUNIZATION_BASE_PATH")):
    non_prod = ["internal-dev", "int", "sandbox"]
    if service_env in non_prod:
        subdomain = f"{service_env}."
    if service_env == "prod":
        subdomain = ""
    else:
        subdomain = "internal-dev."
    return f"https://{subdomain}api.service.nhs.uk/{service_base_path}"


class FhirController:
    immunization_id_pattern = r"^[A-Za-z0-9\-.]{1,64}$"

    def __init__(self, fhir_service: FhirService):
        self.fhir_service = fhir_service

    def get_immunization_by_id(self, aws_event) -> dict:
        imms_id = aws_event["pathParameters"]["id"]

        id_error = self._validate_id(imms_id)
        if id_error:
            return self.create_response(400, id_error)

        resource = self.fhir_service.get_immunization_by_id(imms_id)
        if resource:
            return FhirController.create_response(200, resource.json())
        else:
            msg = "The requested resource was not found."
            id_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                                code=Code.not_found,
                                                diagnostics=msg)
            return FhirController.create_response(404, id_error)

    def create_immunization(self, aws_event):
        try:
            imms = json.loads(aws_event["body"])
        except json.decoder.JSONDecodeError as e:
            return self._create_bad_request(f"Request's body contains malformed JSON: {e}")

        try:
            resource = self.fhir_service.create_immunization(imms)
            location = f"{get_service_url()}/Immunization/{resource.id}"
            return self.create_response(201, None, {"Location": location})
        except ValidationError as error:
            return self.create_response(400, error.to_operation_outcome())
        except UnhandledResponseError as unhandled_error:
            return self.create_response(500, unhandled_error.to_operation_outcome())

    def update_immunization(self, aws_event):
        imms_id = aws_event["pathParameters"]["id"]
        id_error = self._validate_id(imms_id)
        if id_error:
            return FhirController.create_response(400, json.dumps(id_error))
        try:
            imms = json.loads(aws_event["body"])
        except json.decoder.JSONDecodeError as e:
            return self._create_bad_request(f"Request's body contains malformed JSON: {e}")

        try:
            outcome, resource = self.fhir_service.update_immunization(imms_id, imms)
            if outcome == UpdateOutcome.UPDATE:
                return self.create_response(200)
            elif outcome == UpdateOutcome.CREATE:
                location = f"{get_service_url()}/Immunization/{resource.id}"
                return self.create_response(201, None, {"Location": location})
        except ValidationError as error:
            return self.create_response(400, error.to_operation_outcome())

    def delete_immunization(self, aws_event):
        imms_id = aws_event["pathParameters"]["id"]

        id_error = self._validate_id(imms_id)
        if id_error:
            return FhirController.create_response(400, id_error)

        try:
            self.fhir_service.delete_immunization(imms_id)
            return self.create_response(204)
        except ResourceNotFoundError as not_found:
            return self.create_response(404, not_found.to_operation_outcome())
        except UnhandledResponseError as unhandled_error:
            return self.create_response(500, unhandled_error.to_operation_outcome())

    def search_immunizations(self, aws_event) -> dict:
        params = aws_event["queryStringParameters"]

        if "nhsNumber" not in params:
            return self._create_bad_request("Query parameter 'nhsNumber' is mandatory")
        if "diseaseType" not in params:
            return self._create_bad_request("Query parameter 'diseaseType' is mandatory")

        result = self.fhir_service.search_immunizations(params["nhsNumber"], params["diseaseType"])

        return self.create_response(200, result.json())

    def _validate_id(self, _id: str) -> Optional[dict]:
        if not re.match(self.immunization_id_pattern, _id):
            msg = "the provided event ID is either missing or not in the expected format."
            return create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                            code=Code.invalid,
                                            diagnostics=msg)
        else:
            return None

    def _create_bad_request(self, message):
        error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                         code=Code.invalid,
                                         diagnostics=message)
        return self.create_response(400, error)

    @staticmethod
    def create_response(status_code, body=None, headers=None):
        if body:
            if isinstance(body, dict):
                body = json.dumps(body)
            if headers:
                headers["Content-Type"] = "application/fhir+json"
            else:
                headers = {"Content-Type": "application/fhir+json"}

        return {
            "statusCode": status_code,
            "headers": headers if headers else {},
            **({"body": body} if body else {}),
        }
