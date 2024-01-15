"""Practitioner FHIR R4B validator"""
from fhir.resources.R4B.practitioner import Practitioner

from models.utils import (
    pre_validate_list,
    pre_validate_string,
)


class PractitionerValidator:
    """
    Validate the practitioner record against the NHS specific validators and Practitioner
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
        Pre-validate that, if name[0].given (legacy CSV field name:
        PERFORMING_PROFESSIONAL_FORENAME) exists, then it is an array
        containing a single non-empty string
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
        Pre-validate that, if name[0].family (legacy CSV field name:
        PERFORMING_PROFESSIONAL_SURNAME) exists, then it is a non-empty string
        """

        try:
            name_family = values["name"][0]["family"]
            pre_validate_string(name_family, "name[0].family")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier exists, then it is a list of length 1
        """
        try:
            identifier = values["identifier"]
            pre_validate_list(identifier, "identifier", defined_length=1)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0].value (legacy CSV field name:
        PERFORMING_PROFESSIONAL_BODY_REG_CODE) exists, then it is a non-empty string
        """
        try:
            identifier_value = values["identifier"][0]["value"]
            pre_validate_string(identifier_value, "identifier[0].value")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_system(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0].system (legacy CSV field name:
        PERFORMING_PROFESSIONAL_BODY_REG_URI) exists, then it is a non-empty string
        """
        try:
            identifier_system = values["identifier"][0]["system"]
            pre_validate_string(identifier_system, "identifier[0].system")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_type_coding(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0].type.coding exists, then it is a list of length 1
        """
        try:
            identifier_type_coding = values["identifier"][0]["type"]["coding"]
            pre_validate_list(
                identifier_type_coding,
                "identifier[0].type.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_type_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0].type.coding[0].display (legacy CSV field name:
        SDS_JOB_ROLE_NAME) exists, then it is a non-empty string
        """
        try:
            identifier_type_coding_display = values["identifier"][0]["type"]["coding"][
                0
            ]["display"]
            pre_validate_string(
                identifier_type_coding_display,
                "identifier[0].type.coding[0].display",
            )
        except KeyError:
            pass

        return values

    def add_custom_root_validators(self):
        """Add custom NHS validators to the model"""
        Practitioner.add_root_validator(self.pre_validate_name, pre=True)
        Practitioner.add_root_validator(self.pre_validate_name_given, pre=True)
        Practitioner.add_root_validator(self.pre_validate_name_family, pre=True)
        Practitioner.add_root_validator(self.pre_validate_identifier, pre=True)
        Practitioner.add_root_validator(self.pre_validate_identifier_value, pre=True)
        Practitioner.add_root_validator(self.pre_validate_identifier_system, pre=True)
        Practitioner.add_root_validator(
            self.pre_validate_identifier_type_coding, pre=True
        )
        Practitioner.add_root_validator(
            self.pre_validate_identifier_type_coding_display, pre=True
        )

    def validate(self, json_data) -> Practitioner:
        """Generate the Practitioner model from the JSON data"""
        return Practitioner.parse_obj(json_data)
