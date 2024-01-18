import uuid
from dataclasses import dataclass
from enum import Enum

from fhir.resources.R4B.operationoutcome import OperationOutcome


class Severity(str, Enum):
    error = "error"


class Code(str, Enum):
    not_found = "not-found"
    invalid = "invalid"
    server_error = "internal-server-error"
    invariant = "invariant"


@dataclass
class ResourceNotFoundError(RuntimeError):
    """Return this error when the requested FHIR resource does not exist"""
    resource_type: str
    resource_id: str

    def to_operation_outcome(self) -> OperationOutcome:
        msg = f"{self.resource_type} resource does not exit. ID: {self.resource_id}"
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.not_found, diagnostics=msg)


@dataclass
class UnhandledResponseError(RuntimeError):
    """Use this error when the response from an external service (ex: dynamodb) can't be handled"""
    response: dict
    message: str

    def to_operation_outcome(self) -> OperationOutcome:
        msg = f"{self.message}\n{self.response}"
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.server_error, diagnostics=msg)


class ValidationError(RuntimeError):
    def to_operation_outcome(self) -> OperationOutcome:
        pass


@dataclass
class InvalidPatientId(ValidationError):
    """Use this when NHS Number is invalid or doesn't exist"""
    nhs_number: str

    def to_operation_outcome(self) -> OperationOutcome:
        msg = f"NHS Number: {self.nhs_number} is invalid or it doesn't exist."
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.server_error, diagnostics=msg)


@dataclass
class CoarseValidationError(ValidationError):
    """Pre validation error"""
    message: str

    def to_operation_outcome(self) -> OperationOutcome:
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.invariant, diagnostics=self.message)


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
