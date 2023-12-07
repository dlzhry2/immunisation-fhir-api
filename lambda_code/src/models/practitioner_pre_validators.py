"""Pre-validators for Practitioner model"""

from models.utils import (
    generic_list_validation,
    generic_string_validation,
)


class PractitionerPreValidators:
    """Pre-validators for Practitioner model"""

    @staticmethod
    def name(name: list[dict]) -> list[dict]:
        """Pre-validate name"""

        generic_list_validation(name, "name", defined_length=1)

        return name

    @staticmethod
    def name_given(name_given: list[str]) -> list[str]:
        """Pre-validate name[0] -> given (performing_professional_forename(s))"""

        generic_list_validation(name_given, "name[0] -> given")

        for name in name_given:
            if not isinstance(name, str):
                raise TypeError("name[0] -> given must be an array of strings")

            if len(name) == 0:
                raise ValueError(
                    "name[0] -> given must be an array of non-empty strings"
                )

        return name_given

    @staticmethod
    def name_family(name_family: str) -> str:
        """Pre_validate name[0] -> family (performing_professional_surname)"""

        generic_string_validation(name_family, "name[0] -> family")

        return name_family

    @staticmethod
    def identifier(identifier: list[dict]) -> list[dict]:
        """Pre-validate identifier"""

        generic_list_validation(identifier, "identifier", defined_length=1)

        return identifier

    @staticmethod
    def identifier_value(identifier_value: str) -> str:
        """Pre-validate identifier[0] -> value (performing_professional_body_reg_code)"""

        generic_string_validation(identifier_value, "identifier[0] -> value")

        return identifier_value

    @staticmethod
    def identifier_system(identifier_system: str) -> str:
        """Pre-validate identifier[0] -> system (performing_professional_body_reg_uri)"""

        generic_string_validation(identifier_system, "identifier[0] -> system")

        return identifier_system
