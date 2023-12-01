"""Immunization pre-validators"""


class ImmunizationPreValidators:
    @staticmethod
    def pre_patient_identifier_value(patient_identifier_value: str) -> str:
        """Pre-validate patient identifier value"""

        if not isinstance(patient_identifier_value, str):
            raise TypeError("patient -> identifier -> value must be a string")

        if len(patient_identifier_value) != 10:
            raise ValueError("patient -> identifier -> Value must be 10 characters")

        return patient_identifier_value
