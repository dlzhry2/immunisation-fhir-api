import re
from datetime import datetime
from typing import Union
from decimal import Decimal
from mappings import Mandation, vaccination_procedure_snomed_codes


def get_deep_attr(obj, attrs):
    for attr in attrs.split("."):
        obj = getattr(obj, attr)
    return obj


class MandatoryError(Exception):
    def __init__(self, message=None):
        self.message = message


class NotApplicableError(Exception):
    def __init__(self, message=None):
        self.message = message


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
    def check_attribute_exists(
        values, key, attribute, mandation, field_location, index=None
    ):
        try:
            obj = values[key][index] if index is not None else values[key]

            if attribute is not None:
                if not get_deep_attr(obj, attribute):
                    raise AttributeError()
            else:
                field_value = obj
                if field_value is None:
                    if mandation == Mandation.mandatory:
                        raise MandatoryError()

            if mandation == Mandation.not_applicable:
                raise NotApplicableError(
                    f"{field_location} must not be provided for this vaccine type"
                )

        except (KeyError, AttributeError, MandatoryError) as error:
            if mandation == Mandation.mandatory:
                raise MandatoryError(
                    f"{field_location} is a mandatory field"
                ) from error

    @staticmethod
    def check_questionnaire_link_id_exists(
        values, link_id, field_type, mandation, field_location
    ):
        try:
            questionnaire_response = [
                x
                for x in values["contained"]
                if x.resource_type == "QuestionnaireResponse"
            ][0]

            item = [x for x in questionnaire_response.item if x.linkId == link_id][0]

            field_value = get_deep_attr(item.answer[0].valueCoding, field_type)

            if field_value is None:
                if mandation == Mandation.mandatory:
                    raise MandatoryError()

            if mandation == Mandation.not_applicable:
                raise NotApplicableError(
                    f"{field_location} must not be provided for this vaccine type"
                )

        except (KeyError, AttributeError, MandatoryError) as error:
            if mandation == Mandation.mandatory:
                raise MandatoryError(
                    f"{field_location} is a mandatory field"
                ) from error
