import os
import json
from models.errors import UnhandledResponseError
from fhir_service import FhirService
from fhir_repository import ImmunizationRepository, create_table


def make_controller(immunization_env: str = os.getenv("IMMUNIZATION_ENV")):
    endpoint_url = "http://localhost:4566" if immunization_env == "local" else None
    imms_repo = ImmunizationRepository(create_table(endpoint_url=endpoint_url))
    service = FhirService(imms_repo=imms_repo)

    return FhirController(fhir_service=service)


class FhirController:

    def __init__(
        self,
        fhir_service: FhirService,
    ):
        self.fhir_service = fhir_service

    def create_immunization(self, immunisation: any, supplier_system: str):
        try:
            self.fhir_service.create_immunization(immunisation, supplier_system, vax_type)
        except UnhandledResponseError as unhandled_error:
            return self.create_response(500, unhandled_error.to_operation_outcome())

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
