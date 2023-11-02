from enum import Enum

from fhir.resources.operationoutcome import OperationOutcome
from pydantic import BaseModel


class Severity(str, Enum):
    error = "error"


class Code(str, Enum):
    not_found = "NOT_FOUND"


# @dataclass
class ApiError(BaseModel):
    id: str
    severity: Severity
    code: Code
    diagnostics: str


base_model = {
    "resourceType": "OperationOutcome",
    "id": None,
    "meta": {
        "profile": [
            "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
        ]
    },
    "issue": [
        {
            "severity": None,
            "code": None,
            "details": {
                "coding": [
                    {
                        "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                        "code": None
                    }
                ]
            },
            "diagnostics": None
        }
    ]
}


class ApiErrors:
    @staticmethod
    def event_not_found(error: ApiError) -> OperationOutcome:
        op = OperationOutcome.parse_obj(base_model, "fd")
        # op = OperationOutcome.construct()
        # op.id = error_id
        # issue = OperationOutcomeIssue.construct()
        # issue.severity = "error"
        # issue.code = "not_found"
        # op.issue = issue
        return op
