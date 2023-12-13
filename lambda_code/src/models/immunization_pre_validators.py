"""Immunization pre-validators"""
from models.utils import (
    generic_string_validation,
    generic_date_time_validation,
    generic_list_validation,
    generic_date_validation,
    generic_boolean_validation,
    generic_positive_integer_validation,
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

        if " " in patient_identifier_value:
            raise ValueError("patient -> identifier -> value must not contain spaces")

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

    @staticmethod
    def extension_value_codeable_concept_coding(coding: list) -> list:
        """
        Pre-validate extension[*] -> valueCodeableConcept -> coding
        """
        generic_list_validation(
            coding,
            "extension[*] -> valueCodeableConcept -> coding",
            defined_length=1,
        )

        return coding

    @staticmethod
    def vaccination_situation_code(vaccination_situation_code: str) -> str:
        """
        Pre-validate extension[*] ->
        url[https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation]:
        valueCodeableConcept -> coding -> code
        (vaccination_situation_code)
        """

        generic_string_validation(
            vaccination_situation_code,
            "extension[*] -> url["
            + "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation]: "
            + "valueCodeableConcept -> coding[0] -> code",
        )

        return vaccination_situation_code

    @staticmethod
    def vaccination_situation_display(vaccination_situation_display: str) -> str:
        """
        Pre-validate extension[*] ->
        url[https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation]:
        valueCodeableConcept -> coding -> display
        (vaccination_situation_term)
        """

        generic_string_validation(
            vaccination_situation_display,
            "extension[*] -> url["
            + "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation]: "
            + "valueCodeableConcept -> coding[0] -> display",
        )

        return vaccination_situation_display

    @staticmethod
    def status_reason_coding(coding: list) -> list:
        """
        Pre-validate statusReason -> coding (reason_not_given_code)
        """
        generic_list_validation(
            coding,
            "statusReason -> coding",
            defined_length=1,
        )

        return coding

    @staticmethod
    def status_reason_coding_code(status_reason_coding_code: str) -> str:
        """Pre-validate statusReason -> coding[0] -> code (reason_not_given_code)"""

        generic_string_validation(
            status_reason_coding_code, "statusReason -> coding[0] -> code"
        )

        return status_reason_coding_code

    @staticmethod
    def status_reason_coding_display(status_reason_coding_display: str) -> str:
        """Pre_validate statusReason -> coding[0] -> display (reason_not_given_term)"""

        generic_string_validation(
            status_reason_coding_display, "statusReason -> coding[0] -> display"
        )

        return status_reason_coding_display

    @staticmethod
    def protocol_applied_dose_number_positive_int(
        protocol_applied_dose_number_positive_int: int,
    ) -> int:
        """Pre-validate protocolApplied -> doseNumberPositiveInt (dose_sequence)"""

        # Raise error if is not a positive integer
        generic_positive_integer_validation(
            protocol_applied_dose_number_positive_int,
            "protocolApplied -> doseNumberPositiveInt",
        )

        # Raise error if is not in the range 1 to 9
        if protocol_applied_dose_number_positive_int not in range(1, 10):
            raise ValueError(
                "protocolApplied -> doseNumberPositiveInt must be an integer in the range 1 to 9"
            )

        return protocol_applied_dose_number_positive_int
