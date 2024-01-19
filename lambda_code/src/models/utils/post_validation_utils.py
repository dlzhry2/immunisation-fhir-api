import re
from datetime import datetime
from typing import Union
from decimal import Decimal
from vaccine_procedure_snomed_codes import vaccination_procedure_snomed_codes


class PostValidation:
    @classmethod
    def validate_reduce_validation_code(cls, values: dict) -> dict:
        """Validate that reduce_validation_code is a valid code"""

        reduce_validation_code = "False"
        try:
            for record in values["contained"]:
                if record.resourceType == "QuestionnaireResponse":
                    for item in record.item:
                        if item.linkId == "ReduceValidation":
                            reduce_validation_code = item.answer[0].valueCoding.code
        except KeyError:
            pass
        finally:
            cls.reduce_validation_code = reduce_validation_code

        return values

    @staticmethod
    def vaccination_procedure_code(vaccination_procedure_code: str, field_location):
        vaccine_type = vaccination_procedure_snomed_codes.get(
            vaccination_procedure_code, None
        )

        if not vaccine_type:
            raise ValueError(
                f"{field_location}: {vaccination_procedure_code} "
                + "is not a valid code for this service"
            )

        return vaccine_type
