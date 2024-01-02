"""Immunization FHIR R4B validator"""
from fhir.resources.R4B.immunization import Immunization
from models.utils import get_generic_questionnaire_response_value
from models.immunization_pre_validators import (
    ImmunizationPreValidators,
)


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
        format "YYYY-MM-DDThh:mm:ss+zz:zz" or "YYYY-MM-DDThh:mm:ss-zz:zz" (i.e. date and time,
        including timezone offset in hours and minutes), representing a valid datetime

        NOTE: occurrenceDateTime is a mandatory FHIR field. A value of None will be rejected by the
        FHIR model before pre-validators are run.
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
        item[*] -> linkId[SiteCode]: answer[0] -> valueCoding -> code (site_code) exists,
        then it is a non-empty string
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
        item[*] -> linkId[SiteName]: answer[0] -> valueCoding -> code (site_name) exists,
        then it is a non-empty string
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

    @classmethod
    def pre_validate_status(cls, values: dict) -> dict:
        """
        Pre-validate that, if status (action_flag or not_given) exists, then it is a non-empty
        string which is one of the following: completed, entered-in-error, not-done.

        NOTE 1: action_flag and not_given are mutually exclusive i.e. if action_flag is present then
        not_given will be absent and vice versa. The action_flags are 'completed' and 'not-done'.
        The following 1-to-1 mapping applies:
        * not_given is True <---> Status will be set to 'not-done' (and therefore action_flag is
            absent)
        * not_given is False <---> Status will be set to 'completed' or 'entered-in-error' (and
            therefore action_flag is present)

        NOTE 2: Status is a mandatory FHIR field. A value of None will be rejected by the
        FHIR model before pre-validators are run.
        """

        try:
            status = values["status"]
            ImmunizationPreValidators.status(status)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_recorded(cls, values: dict) -> dict:
        """
        Pre-validate that, if recorded (recorded_date) exists, then it is a string in the format
        YYYY-MM-DD, representing a valid date
        """

        try:
            recorded = values["recorded"]
            ImmunizationPreValidators.recorded(recorded)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_primary_source(cls, values: dict) -> dict:
        """Pre-validate that, if primarySource (primary_source) exists, then it is a boolean"""

        try:
            primary_source = values["primarySource"]
            ImmunizationPreValidators.primary_source(primary_source)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_report_origin_text(cls, values: dict) -> dict:
        """
        Pre-validate that, if reportOrigin -> text (report_origin_text)
        exists, then it is a non-empty string with maximum length 100 characters
        """

        try:
            report_origin_text = values["reportOrigin"]["text"]

            ImmunizationPreValidators.report_origin_text(report_origin_text)
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
        Immunization.add_root_validator(self.pre_validate_status, pre=True)
        Immunization.add_root_validator(self.pre_validate_recorded, pre=True)
        Immunization.add_root_validator(self.pre_validate_primary_source, pre=True)
        Immunization.add_root_validator(self.pre_validate_report_origin_text, pre=True)

    def validate(self, json_data) -> Immunization:
        """Generate the Immunization model"""
        immunization = Immunization.parse_obj(json_data)
        return immunization
