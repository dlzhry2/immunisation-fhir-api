import uuid
from dataclasses import dataclass
from enum import Enum

from fhir.resources.operationoutcome import OperationOutcome


class Severity(str, Enum):
    error = "error"


class Code(str, Enum):
    not_found = "not-found"
    invalid = "invalid"
    server_error = "internal-server-error"


@dataclass
class FhirResourceError:
    resource_type: str
    resource_id: str
    message: str


@dataclass
class ResourceNotFoundError(FhirResourceError, RuntimeError):
    """Return this error when the requested FHIR resource does not exist"""

    def to_operation_outcome(self) -> OperationOutcome:
        return create_operation_outcome(
            resource_id=self.resource_id, severity=Severity.error, code=Code.not_found, diagnostics=self.message)


@dataclass
class UnhandledResponseError(RuntimeError):
    """Use this error when the response from an external service (ex: dynamodb) can't be handled"""
    message: str
    response: dict

    def to_operation_outcome(self) -> OperationOutcome:
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.server_error, diagnostics=self.message)


def create_operation_outcome(resource_id: str, severity: Severity, code: Code, diagnostics: str) -> OperationOutcome:
    model = {
        "resourceType": "OperationOutcome",
        "id": resource_id,
        "meta": {
            "profile": [
                "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
            ]
        },
        "issue": [
            {
                "severity": severity,
                "code": code,
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                            "code": code.upper()
                        }
                    ]
                },
                "diagnostics": diagnostics
            }
        ]
    }
    return OperationOutcome.parse_obj(model)
