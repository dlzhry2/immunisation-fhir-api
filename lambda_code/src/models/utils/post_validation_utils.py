import re
from datetime import datetime
from typing import Union
from decimal import Decimal
from vaccine_procedure_snomed_codes import vaccination_procedure_snomed_codes


class PostValidation:
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
