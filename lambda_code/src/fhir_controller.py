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
        return self._resource_or_not_found(resource)

    def delete_immunization(self, aws_event):
        imms_id = aws_event["pathParameters"]["id"]

        id_error = self._validate_id(imms_id)
        if id_error:
            return FhirController.create_response(400, json.dumps(id_error.dict()))

        try:
            resource = self.fhir_service.delete_immunization(imms_id)
            return self._resource_or_not_found(resource)
        except ResourceNotFoundError as not_found:
            return self._create_not_found_response(not_found)
        except UnhandledResponseError as unhandled_error:
            return self._create_server_error_response(unhandled_error)

    def _validate_id(self, _id: str) -> Optional[OperationOutcome]:
        if not re.match(self.immunization_id_pattern, _id):
            msg = "the provided event ID is either missing or not in the expected format."
            return create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                            code=Code.invalid,
                                            diagnostics=msg)
        else:
            return None

    @staticmethod
    def _resource_or_not_found(resource):
        if resource:
            return FhirController.create_response(200, resource.json())
        else:
            msg = "The requested resource was not found."
            id_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                                code=Code.not_found,
                                                diagnostics=msg)
            return FhirController.create_response(404, json.dumps(id_error.dict()))

    @staticmethod
    def _create_not_found_response(error: ResourceNotFoundError):
        msg = f"The requested {error.resource_type}.id: {error.resource_id} was not found."
        id_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                            code=Code.not_found,
                                            diagnostics=msg)
        return FhirController.create_response(404, json.dumps(id_error.dict()))

    @staticmethod
    def _create_server_error_response(error: UnhandledResponseError):
        msg = f"internal-server-error"
        id_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                            code=Code.server_error,
                                            diagnostics=error.message)
        return FhirController.create_response(500, json.dumps(id_error.dict()))

    @staticmethod
    def create_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": body
        }
