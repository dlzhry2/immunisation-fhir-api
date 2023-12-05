"""Immunization FHIR R4B validator"""
from fhir.resources.R4B.immunization import Immunization
from lambda_code.src.models.immunization_pre_validators import (
    ImmunizationPreValidators,
)
from models.constants import Constants


class ImmunizationValidator:
    """
    Validate the FHIR Immunization model against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def pre_validate_patient_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if  patient -> identifier -> value (NHS number) exists,
        then it is a string of 10 characters
        """
        try:
            patient_identifier_value = values["patient"]["identifier"]["value"]
            ImmunizationPreValidators.pre_patient_identifier_value(
                patient_identifier_value
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_occurrence_date_time(cls, values: dict) -> dict:
        """
        Pre-validate that, if occurrenceDateTime exists (date_and_time), then it is a string in the
        format YYYY-MM-DDThh:mm:ss, representing a valid datetime
        """
        try:
            occurrence_date_time = values["occurrenceDateTime"]
            ImmunizationPreValidators.occurrence_date_time(occurrence_date_time)
        except KeyError:
            pass

        return values

    def add_custom_root_validators(self):
        """Add custom NHS validators to the model"""
        Immunization.add_root_validator(
            self.pre_validate_patient_identifier_value, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_occurrence_date_time, pre=True
        )

    def validate(self, json_data) -> Immunization:
        """Generate the Immunization model"""
        immunization = Immunization.parse_obj(json_data)
        return immunization
