import json
import re
import uuid
from typing import Optional

import boto3
from botocore.config import Config
from fhir.resources.operationoutcome import OperationOutcome

from fhir_repository import ImmunisationRepository, create_table
from fhir_service import FhirService
from models.errors import Severity, Code, create_operation_outcome, ResourceNotFoundError, UnhandledResponseError
from pds import PdsService, Authenticator


def make_controller():
    imms_repo = ImmunisationRepository(create_table())
    env = "internal-dev"
    my_config = Config(region_name='eu-west-2')
    pds_service = PdsService(Authenticator(boto3.client('secretsmanager', config=my_config), env), env)
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
            id_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                                code=Code.not_found,
                                                diagnostics=msg)
            return FhirController.create_response(404, json.dumps(id_error.dict()))

    def create_immunization(self, aws_event):
        try:
            imms = json.loads(aws_event["body"])
        except json.decoder.JSONDecodeError as error:
            body = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                            code=Code.invalid,
                                            diagnostics=f"Request's body contains malformed JSON\n{error}")
            return self.create_response(400, body.json())

        try:
            resource = self.fhir_service.create_immunization(imms)
            return self.create_response(201, resource.json())
        except Exception as error:
            body = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                            code=Code.invalid,
                                            diagnostics=f"nhs number is not provided or is invalid\n{error}")
            return self.create_response(400, body.json())

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
            return self.create_response(500, unhandled_error.to_operation_outcome().json())

    def _validate_id(self, _id: str) -> Optional[OperationOutcome]:
        if not re.match(self.immunization_id_pattern, _id):
            msg = "the provided event ID is either missing or not in the expected format."
            return create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                            code=Code.invalid,
                                            diagnostics=msg)
        else:
            return None

    @staticmethod
    def create_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": body
        }
