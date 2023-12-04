"""Pre-validators for Patient model"""

from models.utils import (
    generic_list_validation,
    generic_string_validation,
    generic_date_validation,
)
import re
from datetime import datetime


class PatientPreValidators:
    """Pre-validators for Patient model"""

    @staticmethod
    def name(name: list[dict]) -> list[dict]:
        """Pre-validate name"""

        generic_list_validation(name, "name", defined_length=1)

        return name

    @staticmethod
    def name_given(name_given: list[str]) -> list[str]:
        """Pre-validate name -> given (person forename(s))"""

        generic_list_validation(name_given, "name -> given")

        for name in name_given:
            if not isinstance(name, str):
                raise TypeError("name -> given must be an array of strings")

            if len(name) == 0:
                raise ValueError("name -> given must be an array of non-empty strings")

        return name_given

    @staticmethod
    def name_family(name_family: str) -> str:
        """Pre_validate name -> family (person surname)"""

        generic_string_validation(name_family, "name -> family")

        return name_family

    @staticmethod
    def birth_date(birth_date: str) -> str:
        """Pre_validate birthDate (person DOB)"""

        generic_date_validation(birth_date, "birthDate")

        return birth_date
