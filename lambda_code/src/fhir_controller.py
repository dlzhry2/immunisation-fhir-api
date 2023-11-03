import json
import re
import uuid

from fhir_service import FhirService
from models.errors import ApiError, Severity, Code


class FhirController:
    immunisation_id_pattern = r"^[A-Za-z0-9\-.]{1,64}$"

    def __init__(self, fhir_service: FhirService):
        self.fhir_service = fhir_service

    def get_immunisation_by_id(self, aws_event) -> dict:
        imms_id = aws_event["pathParameters"]["id"]

        if not re.match(self.immunisation_id_pattern, imms_id):
            api_error = ApiError(id=str(uuid.uuid4()), severity=Severity.error, code=Code.invalid,
                                 diagnostics="the provided event ID is either missing or not in the expected format.")
            res_body = api_error.to_uk_core().dict()
            return FhirController._create_response(400, json.dumps(res_body))

        resource = self.fhir_service.get_immunisation_by_id(imms_id)
        if resource:
            return FhirController._create_response(200, resource.json())
        else:
            api_error = ApiError(id=str(uuid.uuid4()), severity=Severity.error, code=Code.not_found,
                                 diagnostics="The requested resource was not found.")
            res_body = api_error.to_uk_core().dict()
            return FhirController._create_response(404, json.dumps(res_body))

    @staticmethod
    def _create_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": body
        }
