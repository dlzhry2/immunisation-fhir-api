import json
import os
import re
import uuid
from typing import Optional

import boto3
import base64
from botocore.config import Config
from fhir.resources.R4B.operationoutcome import OperationOutcome

from cache import Cache
from fhir_repository import ImmunizationRepository, create_table
from fhir_service import FhirService
from models.errors import (
    Severity,
    Code,
    create_operation_outcome,
    ResourceNotFoundError,
    UnhandledResponseError,
    ValidationError,
)
from pds_service import PdsService, Authenticator
import urllib.parse


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
            return self.create_response(400, json.dumps(id_error.dict()))

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
            return FhirController.create_response(404, json.dumps(id_error.dict()))

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
            return self.create_response(400, error.to_operation_outcome().json())
        except UnhandledResponseError as unhandled_error:
            return self.create_response(
                500, unhandled_error.to_operation_outcome().json()
            )

    def delete_immunization(self, aws_event):
        imms_id = aws_event["pathParameters"]["id"]

        id_error = self._validate_id(imms_id)
        if id_error:
            return FhirController.create_response(400, json.dumps(id_error.dict()))

        try:
            resource = self.fhir_service.delete_immunization(imms_id)
            return self.create_response(200, resource.json())
        except ResourceNotFoundError as not_found:
            return self.create_response(404, not_found.to_operation_outcome().json())
        except UnhandledResponseError as unhandled_error:
            return self.create_response(
                500, unhandled_error.to_operation_outcome().json()
            )

    def search_immunizations(self, aws_event) -> dict:
        http_method = aws_event.get("httpMethod")
        nhsNumberValue = None
        diseaseTypeValue = None
        nhsNumberParam = "-nhsNumber"
        diseaseTypeParam = "-diseaseType"

        if http_method == "POST":
            # Check if the Content-Type is application/x-www-form-urlencoded
            content_type = aws_event.get("headers", {}).get("Content-Type")
            if content_type == "application/x-www-form-urlencoded":
                # Parse the body of the request
                body = aws_event["body"]
                # Decode the base64-encoded body
                decoded_body = base64.b64decode(body).decode("utf-8")
                # Parse the decoded body as application/x-www-form-urlencoded
                parsed_body = urllib.parse.parse_qs(decoded_body)
                # Access individual form parameters and check if nhsNumber or diseaseType is present
                nhsNumber_list = parsed_body.get(nhsNumberParam)
                if nhsNumber_list:
                    nhsNumberValue = nhsNumber_list[0]

                diseaseType_list = parsed_body.get(diseaseTypeParam)
                if diseaseType_list:
                    diseaseTypeValue = diseaseType_list[0]
                # Continue processing the request

        params = aws_event["queryStringParameters"]
        # If nhsNumber was not present in body then it should be in params irresepective of GET/POST
        if nhsNumberValue is None:
            if params is None or nhsNumberParam not in params:
                return self._create_bad_request(
                    f"Search Parameter {nhsNumberParam} is mandatory"
                )
            else:
                nhsNumberValue = params[nhsNumberParam]

        # If diseaseType was not present in body then it should be in params irresepective of GET/POST
        if diseaseTypeValue is None:
            if params is None or diseaseTypeParam not in params:
                return self._create_bad_request(
                        f"Search Parameter {diseaseTypeParam} is mandatory"
                )
            else:
                diseaseTypeValue = params[diseaseTypeParam]

        result = self.fhir_service.search_immunizations(
            nhsNumberValue, diseaseTypeValue
        )
        return self.create_response(200, result.json())

    def _validate_id(self, _id: str) -> Optional[OperationOutcome]:
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
        return self.create_response(400, error.json())

    @staticmethod
    def create_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": body,
        }
