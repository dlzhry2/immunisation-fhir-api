"""Pre-validators for Patient model"""

from models.utils import (
    generic_list_validation,
    generic_string_validation,
    generic_date_validation,
)
from models.constants import Constants


class PatientPreValidators:
    """Pre-validators for Patient model"""

    @staticmethod
    def name(name: list[dict]) -> list[dict]:
        """Pre-validate name"""

        generic_list_validation(name, "name", defined_length=1)

        return name

    @staticmethod
    def name_given(name_given: list[str]) -> list[str]:
        """Pre-validate name -> given (person_forename(s))"""

        generic_list_validation(name_given, "name -> given")

        for name in name_given:
            if not isinstance(name, str):
                raise TypeError("name -> given must be an array of strings")

            if len(name) == 0:
                raise ValueError("name -> given must be an array of non-empty strings")

        return name_given

    @staticmethod
    def name_family(name_family: str) -> str:
        """Pre_validate name -> family (person_surname)"""

        generic_string_validation(name_family, "name -> family")

        return name_family

    @staticmethod
    def birth_date(birth_date: str) -> str:
        """Pre_validate birthDate (person_DOB)"""

        generic_date_validation(birth_date, "birthDate")

        return birth_date

    @staticmethod
    def gender(gender: str) -> str:
        """Pre-validate gender (person_gender)"""

        generic_string_validation(gender, "gender", predefined_values=Constants.genders)

        return gender

    @staticmethod
    def address(address: list[dict]) -> list[dict]:
        """Pre-validate address"""

        generic_list_validation(address, "address", defined_length=1)

        return address

    @staticmethod
    def address_postal_code(address_postal_code: str) -> str:
        """Pre-validate address -> postalCode (person_postcode)"""

        generic_string_validation(address_postal_code, "address -> postalCode")

        if len(address_postal_code.split(" ")) != 2:
            raise ValueError(
                "address -> postalCode must be divided into two parts by a single space"
            )

        if len(address_postal_code.replace(" ", "")) > 8:
            raise ValueError(
                "address -> postalCode must be 8 or fewer characters (excluding spaces)"
            )

        return address_postal_code
