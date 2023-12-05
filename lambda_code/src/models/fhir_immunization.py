"""Immunization FHIR R4B validator"""
from fhir.resources.R4B.immunization import Immunization
from lambda_code.src.models.immunization_pre_validators import (
    ImmunizationPreValidators,
)
from models.constants import Constants
from models.utils import get_generic_questionnaire_response_value


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
            ImmunizationPreValidators.patient_identifier_value(patient_identifier_value)
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

    @classmethod
    def pre_validate_contained(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained exists, then it is a list of length 1
        """
        try:
            contained = values["contained"]
            ImmunizationPreValidators.contained(contained)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_questionnaire_answers(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[0] -> resourceType[QuestionnaireResponse]:
        item[*] -> linkId[*]: answer is a list of length 1
        """

        try:
            for item in values["contained"][0]["item"]:
                try:
                    answer = item["answer"]
                    ImmunizationPreValidators.questionnaire_answer(answer)
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_questionnaire_site_code_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[0] -> resourceType[QuestionnaireResponse]:
        item[*] -> linkId[SiteCode]: answer[0] -> valueCoding -> code exists,
        then it is a string
        """
        try:
            questionnaire_site_code_code = get_generic_questionnaire_response_value(
                values, "SiteCode", "code"
            )
            ImmunizationPreValidators.questionnaire_site_code_code(
                questionnaire_site_code_code
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_site_name_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[0] -> resourceType[QuestionnaireResponse]:
        item[*] -> linkId[SiteName]: answer[0] -> valueCoding -> code exists,
        then it is a string
        """
        try:
            questionnaire_site_name_code = get_generic_questionnaire_response_value(
                values, "SiteName", "code"
            )
            ImmunizationPreValidators.questionnaire_site_name_code(
                questionnaire_site_name_code
            )
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
            ImmunizationPreValidators.identifier(identifier)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0] -> value (unique_id) exists,
        then it is a non-empty string
        """
        try:
            identifier_value = values["identifier"][0]["value"]
            ImmunizationPreValidators.identifier_value(identifier_value)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_system(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0] -> system (unique_id_uri) exists,
        then it is a non-empty string
        """
        try:
            identifier_system = values["identifier"][0]["system"]
            ImmunizationPreValidators.identifier_system(identifier_system)
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
        Immunization.add_root_validator(self.pre_validate_contained, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_questionnaire_answers, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_questionnaire_site_code_code, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_site_name_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_identifier, pre=True)
        Immunization.add_root_validator(self.pre_validate_identifier_value, pre=True)
        Immunization.add_root_validator(self.pre_validate_identifier_system, pre=True)

    def validate(self, json_data) -> Immunization:
        """Generate the Immunization model"""
        immunization = Immunization.parse_obj(json_data)
        return immunization
