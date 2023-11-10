from dataclasses import dataclass
from enum import Enum

from fhir.resources.operationoutcome import OperationOutcome


@dataclass
class FhirResourceError:
    resource_type: str
    resource_id: str
    message: str


@dataclass
class ResourceNotFoundError(FhirResourceError, RuntimeError):
    """Return this error when the requested FHIR resource from client does not exist"""
    pass


@dataclass
class UnhandledResponseError(RuntimeError):
    """Use this error when the response from an external service (ex dynamodb) can't be handled"""
    message: str
    response: dict


class Severity(str, Enum):
    error = "error"


class Code(str, Enum):
    not_found = "not-found"
    invalid = "invalid"


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
