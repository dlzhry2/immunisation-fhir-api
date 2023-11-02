from enum import Enum

from fhir.resources.operationoutcome import OperationOutcome
from pydantic import BaseModel


class Severity(str, Enum):
    error = "error"


class Code(str, Enum):
    not_found = "not_found"


class ApiError(BaseModel, use_enum_values=True):
    id: str
    severity: Severity
    code: Code
    diagnostics: str

    def to_uk_core(self) -> OperationOutcome:
        model = {
            "resourceType": "OperationOutcome",
            "id": self.id,
            "meta": {
                "profile": [
                    "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
                ]
            },
            "issue": [
                {
                    "severity": self.severity,
                    "code": self.code,
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                                "code": self.code.upper()
                            }
                        ]
                    },
                    "diagnostics": self.diagnostics
                }
            ]
        }
        return OperationOutcome.parse_obj(model)
