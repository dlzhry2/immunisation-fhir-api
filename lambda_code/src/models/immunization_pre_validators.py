"""Immunization pre-validators"""
from models.utils import generic_string_validation, generic_date_time_validation


class ImmunizationPreValidators:
    @staticmethod
    def pre_patient_identifier_value(patient_identifier_value: str) -> str:
        """Pre-validate patient -> identifier value (NHS_number)"""

        generic_string_validation(
            patient_identifier_value,
            "patient -> identifier -> value",
            defined_length=10,
        )

        return patient_identifier_value

    @staticmethod
    def occurrence_date_time(occurrence_date_time: str) -> str:
        """Pre_validate occurrenceDateTime (date_and_time)"""

        generic_date_time_validation(occurrence_date_time, "occurrenceDateTime")

        return occurrence_date_time
