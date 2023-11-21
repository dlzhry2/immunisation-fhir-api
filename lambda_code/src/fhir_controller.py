import json
import re
import uuid
from fhir_service import FhirService
from models.errors import Severity, Code, create_operation_outcome
from pds import PdsService


class FhirController:
    immunisation_id_pattern = r"^[A-Za-z0-9\-.]{1,64}$"

    def __init__(self, fhir_service: FhirService, pds_service: PdsService):
        self.fhir_service = fhir_service
        self.pds_service = pds_service

    def get_immunisation_by_id(self, aws_event) -> dict:
        imms_id = aws_event["pathParameters"]["id"]

        if not re.match(self.immunisation_id_pattern, imms_id):
            msg = "the provided event ID is either missing or not in the expected format."
            api_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                                 code=Code.invalid,
                                                 diagnostics=msg)
            return FhirController.create_response(400, json.dumps(api_error.dict()))

        patient_details = self.pds_service.get_patient_details(imms_id)

        if patient_details.status_code == 200:
            print(patient_details)
            
        resource = self.fhir_service.get_immunisation_by_id(imms_id)
        
        if resource:
            return FhirController.create_response(200, resource.json())
        else:
            msg = "The requested resource was not found."
            api_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                                    code=Code.not_found,
                                                    diagnostics=msg)
            return FhirController.create_response(404, json.dumps(api_error.dict()))

    @staticmethod
    def create_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": body
        }
