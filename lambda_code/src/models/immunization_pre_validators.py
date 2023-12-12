"""Immunization pre-validators"""
from models.utils import (
    generic_string_validation,
    generic_date_time_validation,
    generic_list_validation,
    generic_date_validation,
    generic_boolean_validation,
)

from models.constants import Constants


class ImmunizationPreValidators:
    """Pre-validators for Immunization model"""

    @staticmethod
    def patient_identifier_value(patient_identifier_value: str) -> str:
        """Pre-validate patient -> identifier value (NHS_number)"""

        generic_string_validation(
            patient_identifier_value,
            "patient -> identifier -> value",
            defined_length=10,
        )

        if not patient_identifier_value.isdigit():
            raise ValueError("patient -> identifier -> value must only contain digits")

        return patient_identifier_value

    @staticmethod
    def occurrence_date_time(occurrence_date_time: str) -> str:
        """Pre_validate occurrenceDateTime (date_and_time)"""

        generic_date_time_validation(occurrence_date_time, "occurrenceDateTime")

        return occurrence_date_time

    @staticmethod
    def contained(contained: list) -> list:
        """Pre-validate contained"""

        generic_list_validation(contained, "contained", defined_length=1)

        return contained

    @staticmethod
    def questionnaire_answer(questionnaire_answer: list) -> list:
        """
        Pre-validate contained[0] -> resourceType[QuestionnaireResponse]:
        item[*] -> linkId[*]: answer
        """

        generic_list_validation(
            questionnaire_answer,
            "contained[0] -> resourceType[QuestionnaireResponse]: item[*] -> linkId[*]: answer",
            defined_length=1,
        )

        return questionnaire_answer

    @staticmethod
    def questionnaire_site_code_code(questionnaire_site_code_code: str) -> str:
        """
        Pre-validate contained[0] -> resourceType[QuestionnaireResponse]:
        item[*] -> linkId[SiteCode]:
        answer[0] -> valueCoding -> code
        (site_code)
        """

        generic_string_validation(
            questionnaire_site_code_code,
            "contained[0] -> resourceType[QuestionnaireResponse]: "
            + "item[*] -> linkId[SiteCode]: answer[0] -> valueCoding -> code",
        )

        return questionnaire_site_code_code

    @staticmethod
    def questionnaire_site_name_code(questionnaire_site_name_code: str) -> str:
        """
        Pre-validate contained[0] -> resourceType[QuestionnaireResponse]:
        item[*] -> linkId[SiteName]:
        answer[0] -> valueCoding -> code
        (site_name)
        """

        generic_string_validation(
            questionnaire_site_name_code,
            "contained[0] -> resourceType[QuestionnaireResponse]: "
            + "item[*] -> linkId[SiteName]: answer[0] -> valueCoding -> code",
        )

        return questionnaire_site_name_code

    @staticmethod
    def identifier(identifier: list[dict]) -> list[dict]:
        """Pre-validate identifier"""

        generic_list_validation(identifier, "identifier", defined_length=1)

        return identifier

    @staticmethod
    def identifier_value(identifier_value: str) -> str:
        """Pre-validate identifier[0] -> value (unique_id)"""

        generic_string_validation(identifier_value, "identifier[0] -> value")

        return identifier_value

    @staticmethod
    def identifier_system(identifier_system: str) -> str:
        """Pre-validate identifier[0] -> system (unique_id_uri)"""

        generic_string_validation(identifier_system, "identifier[0] -> system")

        return identifier_system

    @staticmethod
    def status(status: str) -> str:
        """Pre-validate status (action_flag)"""

        generic_string_validation(
            status, "status", predefined_values=Constants.STATUSES
        )

        return status

    @staticmethod
    def recorded(recorded: str) -> str:
        """Pre_validate recorded (recorded_date)"""

        generic_date_validation(recorded, "recorded")

        return recorded

    @staticmethod
    def primary_source(primary_source: bool) -> bool:
        """Pre_validate primarySource (primary_source)"""

        generic_boolean_validation(primary_source, "primarySource")

        return primary_source

    @staticmethod
    def report_origin_text(report_origin_text: str) -> str:
        """Pre_validate reportOrigin -> text (report_origin)"""

        generic_string_validation(
            report_origin_text, "reportOrigin -> text", max_length=100
        )

        return report_origin_text
