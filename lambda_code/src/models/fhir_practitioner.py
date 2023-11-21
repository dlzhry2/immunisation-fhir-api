"""Practitioner FHIR R4B validator"""
from fhir.resources.R4B.practitioner import Practitioner
from models.nhs_validators import NHSPractitionerValidators


class PractitionerValidator:
    """
    Validate the practitioner record against the NHS specific validators and Practitioner
    FHIR profile
    """

    def __init__(self, json_data) -> None:
        self.json_data = json_data

    @classmethod
    def validate_performing_professional_forename(cls, values: dict) -> dict:
        """Validate Performing Professional Forename"""
        performing_professional_forename = values.get("name")[0].given[0]
        performing_professional_surname = values.get("name")[0].family
        NHSPractitionerValidators.validate_performing_professional_forename(
            performing_professional_forename, performing_professional_surname
        )
        return values

    @classmethod
    def validate_performing_professional_body_reg_code(cls, values: dict) -> dict:
        """Validate Performing Professional Body Reg Code"""
        performing_professional_body_reg_code = values.get("identifier")[0].value
        performing_professional_body_reg_uri = values.get("identifier")[0].system
        NHSPractitionerValidators.validate_performing_professional_body_reg_code(
            performing_professional_body_reg_code, performing_professional_body_reg_uri
        )
        return values

    def validate(self) -> Practitioner:
        """
        Add custom NHS validators to the Practitioner model then generate the Practitioner model
        from the JSON data
        """
        # Custom NHS validators
        Practitioner.add_root_validator(self.validate_performing_professional_forename)
        Practitioner.add_root_validator(
            self.validate_performing_professional_body_reg_code
        )

        # Generate the Practitioner model from the JSON data
        practitioner = Practitioner.parse_obj(self.json_data)

        return practitioner
