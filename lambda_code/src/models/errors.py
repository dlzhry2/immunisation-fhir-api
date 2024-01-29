import uuid
from dataclasses import dataclass
from enum import Enum


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

    def to_operation_outcome(self) -> dict:
        msg = f"{self.resource_type} resource does not exit. ID: {self.resource_id}"
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.not_found, diagnostics=msg)


@dataclass
class UnhandledResponseError(RuntimeError):
    """Use this error when the response from an external service (ex: dynamodb) can't be handled"""
    response: dict
    message: str

    def to_operation_outcome(self) -> dict:
        msg = f"{self.message}\n{self.response}"
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.server_error, diagnostics=msg)


class ValidationError(RuntimeError):
    def to_operation_outcome(self) -> dict:
        pass


@dataclass
class InvalidPatientId(ValidationError):
    """Use this when NHS Number is invalid or doesn't exist"""
    nhs_number: str

    def to_operation_outcome(self) -> dict:
        msg = f"NHS Number: {self.nhs_number} is invalid or it doesn't exist."
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.server_error, diagnostics=msg)


@dataclass
class CoarseValidationError(ValidationError):
    """Pre validation error"""
    message: str

    def to_operation_outcome(self) -> dict:
        return create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.invariant, diagnostics=self.message)


def create_operation_outcome(resource_id: str, severity: Severity, code: Code, diagnostics: str) -> dict:
    """Create an OperationOutcome object. Do not use `fhir.resource` library since it adds unnecessary validations"""
    return {
        "resourceType": "OperationOutcome",
        "id": resource_id,
        "issue": [
            {
                "severity": severity,
                "code": code,
                "diagnostics": diagnostics
            }
        ]
    }
