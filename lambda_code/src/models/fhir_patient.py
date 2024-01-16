"""Patient FHIR R4B validator"""

from fhir.resources.R4B.patient import Patient

from models.utils import (
    pre_validate_list,
    pre_validate_string,
    pre_validate_date,
)
from models.constants import Constants


class PatientValidator:
    """
    Validate the patient record against the NHS specific validators and Patient
    FHIR profile
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def pre_validate_name(cls, values: dict) -> dict:
        """Pre-validate that, if name exists, then it is an array of length 1"""
        try:
            name = values["name"]
            pre_validate_list(name, "name", defined_length=1)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_name_given(cls, values: dict) -> dict:
        """
        Pre-validate that, if name[0].given (legacy CSV field name: PERSON_FORENAME) exists, then it is a
        an array containing a single non-empty string
        """
        try:
            name_given = values["name"][0]["given"]
            pre_validate_list(
                name_given,
                "name[0].given",
                defined_length=1,
                elements_are_strings=True,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_name_family(cls, values: dict) -> dict:
        """
        Pre-validate that, if name[0].family (legacy CSV field name: PERSON_SURNAME) exists,
        then it is a non-empty string
        """

        try:
            name_family = values["name"][0]["family"]
            pre_validate_string(name_family, "name[0].family")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_birth_date(cls, values: dict) -> dict:
        """
        Pre-validate that, if birthDate (legacy CSV field name: PERSON_DOB) exists, then it is a
        string in the format YYYY-MM-DD, representing a valid date
        """

        try:
            birth_date = values["birthDate"]
            pre_validate_date(birth_date, "birthDate")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_gender(cls, values: dict) -> dict:
        """
        Pre-validate that, if gender (legacy CSV field name: PERSON_GENDER_CODE) exists,
        then it is a string, which is one of the following: male, female, other, unknown
        """

        try:
            gender = values["gender"]
            pre_validate_string(gender, "gender", predefined_values=Constants.GENDERS)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_address(cls, values: dict) -> dict:
        """Pre-validate that, if address exists, then it is an array of length 1"""
        try:
            address = values["address"]
            pre_validate_list(address, "address", defined_length=1)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_address_postal_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if address[0].postalCode (legacy CSV field name: PERSON_POSTCODE)
        exists, then it is a non-empty string, separated into two parts by a single space
        """

        try:
            address_postal_code = values["address"][0]["postalCode"]
            pre_validate_string(
                address_postal_code, "address[0].postalCode", is_postal_code=True
            )
        except KeyError:
            pass

        return values

    def add_custom_root_validators(self):
        """Add custom NHS validators to the model"""
        Patient.add_root_validator(self.pre_validate_name, pre=True)
        Patient.add_root_validator(self.pre_validate_name_given, pre=True)
        Patient.add_root_validator(self.pre_validate_name_family, pre=True)
        Patient.add_root_validator(self.pre_validate_birth_date, pre=True)
        Patient.add_root_validator(self.pre_validate_gender, pre=True)
        Patient.add_root_validator(self.pre_validate_address, pre=True)
        Patient.add_root_validator(self.pre_validate_address_postal_code, pre=True)

    def validate(self, json_data) -> Patient:
        """Generate the Patient model from the JSON data"""
        return Patient.parse_obj(json_data)
