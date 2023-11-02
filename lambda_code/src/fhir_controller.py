from dataclasses import dataclass

from fhir.resources.resource import Resource


@dataclass
class FhirResponse:
    headers: dict
    body: Resource
    status_code: int


class FhirController:

    def __init__(self, fhir_service):
        self.fhir_service = fhir_service

    def get_immunisation_by_id(self, aws_event) -> FhirResponse:
        pass

    @staticmethod
    def _create_response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": body
        }
