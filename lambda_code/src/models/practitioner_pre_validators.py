"""Pre-validators for Practitioner model"""

from models.utils import (
    pre_validate_list,
    pre_validate_string,
)


class PractitionerPreValidators:
    """Pre-validators for Practitioner model"""

    @staticmethod
    def name(name: list[dict]) -> list[dict]:
        """Pre-validate name"""

        pre_validate_list(name, "name", defined_length=1)

        return name

    @staticmethod
    def name_given(name_given: list[str]) -> list[str]:
        """Pre-validate name[0] -> given (performing_professional_forename(s))"""

        pre_validate_list(name_given, "name[0] -> given", defined_length=1)

        if not isinstance(name_given[0], str):
            raise TypeError("name[0] -> given must be an array of strings")

        if len(name_given[0]) == 0:
            raise ValueError("name[0] -> given must be an array of non-empty strings")

        return name_given

    @staticmethod
    def name_family(name_family: str) -> str:
        """Pre_validate name[0] -> family (performing_professional_surname)"""

        pre_validate_string(name_family, "name[0] -> family")

        return name_family

    @staticmethod
    def identifier(identifier: list[dict]) -> list[dict]:
        """Pre-validate identifier"""

        pre_validate_list(identifier, "identifier", defined_length=1)

        return identifier

    @staticmethod
    def identifier_value(identifier_value: str) -> str:
        """Pre-validate identifier[0] -> value (performing_professional_body_reg_code)"""

        pre_validate_string(identifier_value, "identifier[0] -> value")

        return identifier_value

    @staticmethod
    def identifier_system(identifier_system: str) -> str:
        """Pre-validate identifier[0] -> system (performing_professional_body_reg_uri)"""

        pre_validate_string(identifier_system, "identifier[0] -> system")

        return identifier_system

    @staticmethod
    def identifier_type_coding(identifier_type_coding: list) -> list:
        "Pre-validate identifier[0] -> type -> coding"

        pre_validate_list(
            identifier_type_coding, "identifier[0] -> type -> coding", defined_length=1
        )

        return identifier_type_coding

    @staticmethod
    def identifier_type_coding_display(identifier_type_coding_display: list) -> list:
        "Pre-validate identifier[0] -> type -> coding[0] -> display (sds_job_role_name)"

        pre_validate_string(
            identifier_type_coding_display,
            "identifier[0] -> type -> coding[0] -> display",
        )

        return identifier_type_coding_display
