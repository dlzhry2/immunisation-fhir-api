import json
import os
import re
import uuid
from typing import Optional

import boto3
import base64
from botocore.config import Config

from cache import Cache
from fhir_repository import ImmunizationRepository, create_table
from fhir_service import FhirService, UpdateOutcome
from models.errors import (
    Severity,
    Code,
    create_operation_outcome,
    ResourceNotFoundError,
    UnhandledResponseError,
    ValidationError,
)
from pds_service import PdsService, Authenticator
from urllib.parse import parse_qs


def make_controller(pds_env: str = os.getenv("PDS_ENV", "int")):
    imms_repo = ImmunizationRepository(create_table())
    boto_config = Config(region_name="eu-west-2")
    cache = Cache(directory="/tmp")
    authenticator = Authenticator(
        boto3.client("secretsmanager", config=boto_config), pds_env, cache
    )
    pds_service = PdsService(authenticator, pds_env)

    service = FhirService(imms_repo=imms_repo, pds_service=pds_service)

    return FhirController(fhir_service=service)


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
            id_error = create_operation_outcome(
                resource_id=str(uuid.uuid4()),
                severity=Severity.error,
                code=Code.not_found,
                diagnostics=msg,
            )
            return FhirController.create_response(404, id_error)

    def create_immunization(self, aws_event):
        try:
            imms = json.loads(aws_event["body"])
        except json.decoder.JSONDecodeError as e:
            return self._create_bad_request(
                f"Request's body contains malformed JSON: {e}"
            )

        try:
            resource = self.fhir_service.create_immunization(imms)
            return self.create_response(201, resource.json())
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
            return self._create_bad_request(
                f"Request's body contains malformed JSON: {e}"
            )

        try:
            outcome = self.fhir_service.update_immunization(imms_id, imms)
            if outcome == UpdateOutcome.UPDATE:
                return self.create_response(200)
            elif outcome == UpdateOutcome.CREATE:
                return self.create_response(201)
        except ValidationError as error:
            return self.create_response(400, error.to_operation_outcome())

    def delete_immunization(self, aws_event):
        imms_id = aws_event["pathParameters"]["id"]

        id_error = self._validate_id(imms_id)
        if id_error:
            return FhirController.create_response(400, id_error)

        try:
            resource = self.fhir_service.delete_immunization(imms_id)
            return self.create_response(200, resource.json())
        except ResourceNotFoundError as not_found:
            return self.create_response(404, not_found.to_operation_outcome())
        except UnhandledResponseError as unhandled_error:
            return self.create_response(500, unhandled_error.to_operation_outcome())

    def search_immunizations(self, aws_event) -> dict:
        http_method = aws_event.get("httpMethod")
        nhs_number_list = []
        disease_type_list = []
        nhs_number_param = "-nhsNumber"
        disease_type_param = "-diseaseType"
        if http_method == "POST":
            content_type = aws_event.get("headers", {}).get("Content-Type")
            if content_type == "application/x-www-form-urlencoded":
                body = aws_event["body"]
                decoded_body = base64.b64decode(body).decode("utf-8")
                parsed_body = parse_qs(decoded_body)
                nhs_number_list = parsed_body.get(nhs_number_param)
                disease_type_list = parsed_body.get(disease_type_param)
                
        parsed_query_params = aws_event.get("queryStringParameters", {})
        # AWS API Gateway doesnot support multiple query string parameters with the same name, so it will not be array
        if not parsed_query_params.get(nhs_number_param) in nhs_number_list:
            nhs_number_list.append(parsed_query_params.get(nhs_number_param))

        if not parsed_query_params.get(disease_type_param) in disease_type_list:
            disease_type_list.append(parsed_query_params.get(disease_type_param))

        if not nhs_number_list or (
            len(nhs_number_list) == 1 and nhs_number_list[0] is None
        ):
            return self._create_bad_request(
                f"Search Parameter {nhs_number_param} is mandatory"
            )
        if len(nhs_number_list) > 1:
            return self._create_bad_request(
                f"Search Parameter {nhs_number_param} can have only one value"
            )

        if not disease_type_list or (
            len(disease_type_list) == 1 and disease_type_list[0] is None
        ):
            return self._create_bad_request(
                f"Search Parameter {disease_type_param} is mandatory"
            )
        if len(disease_type_list) > 1:
            return self._create_bad_request(
                f"Search Parameter {disease_type_param} can have only one value"
            )
        search_params = f"{nhs_number_param}={nhs_number_list[0]}&{disease_type_param}={disease_type_list[0]}"
        result = self.fhir_service.search_immunizations(
            nhs_number_list[0], disease_type_list[0], search_params
        )
        return self.create_response(200, result.json())

    def _validate_id(self, _id: str) -> Optional[dict]:
        if not re.match(self.immunization_id_pattern, _id):
            msg = (
                "the provided event ID is either missing or not in the expected format."
            )
            return create_operation_outcome(
                resource_id=str(uuid.uuid4()),
                severity=Severity.error,
                code=Code.invalid,
                diagnostics=msg,
            )
        else:
            return None

    def _create_bad_request(self, message):
        error = create_operation_outcome(
            resource_id=str(uuid.uuid4()),
            severity=Severity.error,
            code=Code.invalid,
            diagnostics=message,
        )
        return self.create_response(400, error)

    @staticmethod
    def create_response(status_code, body=None):
        response = {
            "statusCode": status_code,
            "headers": {},
        }
        if body:
            if isinstance(body, dict):
                body = json.dumps(body)
            response["body"] = body
            response["headers"]["Content-Type"] = "application/fhir+json"
            return response
        else:
            return response
