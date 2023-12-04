"""Immunization pre-validators"""
from models.utils import generic_string_validation


class ImmunizationPreValidators:
    @staticmethod
    def pre_patient_identifier_value(patient_identifier_value: str) -> str:
        """Pre-validate patient identifier value"""

        generic_string_validation(
            patient_identifier_value,
            "patient -> identifier -> value",
            defined_length=10,
        )

        return patient_identifier_value
