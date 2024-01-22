import re
from datetime import datetime
from typing import Union
from decimal import Decimal
from mappings import vaccination_procedure_snomed_codes


def get_deep_attr(obj, attrs):
    for attr in attrs.split("."):
        obj = getattr(obj, attr)
    return obj


class PostValidation:
    @staticmethod
    def vaccination_procedure_code(vaccination_procedure_code: str, field_location):
        vaccine_type = vaccination_procedure_snomed_codes.get(
            vaccination_procedure_code, None
        )

        if not vaccine_type:
            raise ValueError(
                f"{field_location}: {vaccination_procedure_code} "
                + "is not a valid code for this service"
            )

        return vaccine_type

    @staticmethod
    def check_attribute_exists(values, key, attribute, mandation, field_location):
        try:
            if not get_deep_attr(values[key], attribute):
                raise AttributeError()
            if mandation == "N/A":
                raise ValueError(
                    f"{field_location} must not be provided for this vaccine type"
                )
        except (KeyError, AttributeError) as error:
            if mandation == "M":
                raise ValueError(f"{field_location} is a mandatory field") from error
