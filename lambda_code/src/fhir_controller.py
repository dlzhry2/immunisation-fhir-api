import json
import re
import uuid
from typing import Optional

from fhir.resources.operationoutcome import OperationOutcome

from fhir_repository import ImmunisationRepository, create_table
from fhir_service import FhirService
from models.errors import Severity, Code, create_operation_outcome, ResourceNotFoundError, UnhandledResponseError


def make_controller():
    imms_repo = ImmunisationRepository(create_table())
    service = FhirService(imms_repo=imms_repo)
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
        except json.decoder.JSONDecodeError:
            return self._create_bad_request("Request's body contains malformed JSON")

        resource = self.fhir_service.create_immunization(imms)
        return self.create_response(201, resource.json())

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

    def search_immunizations(self, aws_event) -> dict:
        params = aws_event["queryStringParameters"]

        if "nhsNumber" not in params:
            return self._create_bad_request("Query parameter 'nhsNumber' is mandatory")
        if "diseaseType" not in params:
            return self._create_bad_request("Query parameter 'diseaseType' is mandatory")

        result = self.fhir_service.search_immunizations(params["nhsNumber"], params["diseaseType"])

        return self.create_response(200, result.json())

    def _validate_id(self, _id: str) -> Optional[OperationOutcome]:
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
        return self.create_response(400, error.json())

    @staticmethod
    def create_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": body
        }
