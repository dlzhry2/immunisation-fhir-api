"""Generic utilities for models"""

import re
from datetime import datetime
from typing import Literal, Union
from decimal import Decimal


def pre_validate_string(
    field_value: str,
    field_location: str,
    defined_length: int = None,
    max_length: int = None,
    predefined_values: tuple = None,
    is_postal_code: bool = False,
    spaces_allowed: bool = True,
):
    """
    Apply pre-validation to a string field to ensure it is a non-empty string which meets
    the length requirements and predefined values requirements
    """
    if not isinstance(field_value, str):
        raise TypeError(f"{field_location} must be a string")

    if defined_length:
        if len(field_value) != defined_length:
            raise ValueError(f"{field_location} must be {defined_length} characters")
    else:
        if len(field_value) == 0:
            raise ValueError(f"{field_location} must be a non-empty string")

    if max_length:
        if len(field_value) > max_length:
            raise ValueError(
                f"{field_location} must be {max_length} or fewer characters"
            )

    if predefined_values:
        if field_value not in predefined_values:
            raise ValueError(
                f"{field_location} must be one of the following: "
                + str(", ".join(predefined_values))
            )

    if is_postal_code:
        # Validate that field_value contains a single space which divides the two parts
        # of the postal code
        if (
            field_value.count(" ") != 1
            or field_value.startswith(" ")
            or field_value.endswith(" ")
        ):
            raise ValueError(
                f"{field_location} must contain a single space, "
                + "which divides the two parts of the postal code"
            )

        # Validate that max length is 8 (excluding the space)
        if len(field_value.replace(" ", "")) > 8:
            raise ValueError(
                f"{field_location} must be 8 or fewer characters (excluding spaces)"
            )

    if not spaces_allowed:
        if " " in field_value:
            raise ValueError(f"{field_location} must not contain spaces")


def pre_validate_list(
    field_value: list,
    field_location: str,
    defined_length: int = None,
    elements_are_strings: bool = False,
):
    """
    Apply pre-validation to a list field to ensure it is a non-empty list which meets
    the length requirements and requirements, if applicable, for each list element to be a string
    """
    if not isinstance(field_value, list):
        raise TypeError(f"{field_location} must be an array")

    if defined_length:
        if len(field_value) != defined_length:
            raise ValueError(
                f"{field_location} must be an array of length {defined_length}"
            )
    else:
        if len(field_value) == 0:
            raise ValueError(f"{field_location} must be a non-empty array")

    if elements_are_strings:
        for element in field_value:
            if not isinstance(element, str):
                raise TypeError(f"{field_location} must be an array of strings")
            if len(element) == 0:
                raise ValueError(
                    f"{field_location} must be an array of non-empty strings"
                )


def pre_validate_date(field_value: str, field_location: str):
    """
    Apply pre-validation to a date field to ensure that it is a string (JSON dates must be
    written as strings) containing a valid date in the format "YYYY-MM-DD"
    """
    if not isinstance(field_value, str):
        raise TypeError(f"{field_location} must be a string")

    try:
        datetime.strptime(field_value, "%Y-%m-%d").date()
    except ValueError as value_error:
        raise ValueError(
            f"{field_location} must be a valid date string in the format "
            + '"YYYY-MM-DD"'
        ) from value_error


def pre_validate_date_time(field_value: str, field_location: str):
    """
    Apply pre-validation to a datetime field to ensure that it is a string (JSON dates must be
    written as strings) containing a valid datetime in the format "YYYY-MM-DDThh:mm:ss+zz:zz" or
    "YYYY-MM-DDThh:mm:ss-zz:zz" (i.e. date and time, including timezone offset in hours and minutes)
    """

    if not isinstance(field_value, str):
        raise TypeError(f"{field_location} must be a string")

    date_time_pattern_with_timezone = re.compile(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\+|-)\d{2}:\d{2}"
    )

    if not date_time_pattern_with_timezone.fullmatch(field_value):
        raise ValueError(
            f'{field_location} must be a string in the format "YYYY-MM-DDThh:mm:ss+zz:zz" or'
            + '"YYYY-MM-DDThh:mm:ss-zz:zz" (i.e date and time, including timezone offset in '
            + "hours and minutes)"
        )

    try:
        datetime.strptime(field_value, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError as value_error:
        raise ValueError(f"{field_location} must be a valid datetime") from value_error


def pre_validate_boolean(field_value: str, field_location: str):
    """Apply pre-validation to a boolean field to ensure that it is a boolean"""
    if not isinstance(field_value, bool):
        raise TypeError(f"{field_location} must be a boolean")


def pre_validate_positive_integer(
    field_value: int, field_location: str, max_value: int = None
):
    """
    Apply pre-validation to an integer field to ensure that it is a positive integer,
    which does not exceed the maximum allowed value (if applicable)
    """
    if type(field_value) != int:  # pylint: disable=unidiomatic-typecheck
        raise TypeError(f"{field_location} must be a positive integer")

    if field_value <= 0:
        raise ValueError(f"{field_location} must be a positive integer")

    if max_value:
        if field_value not in range(1, max_value + 1):
            raise ValueError(
                f"{field_location} must be an integer in the range 1 to {max_value}"
            )


def pre_validate_decimal(
    field_value: int, field_location: str, max_decimal_places: int = None
):
    """
    Apply pre-validation to a decimal field to ensure that it is an integer or decimal,
    which does not exceed the maximum allowed number of decimal places (if applicable)
    """
    if not (
        type(field_value) is int  # pylint: disable=unidiomatic-typecheck
        or type(field_value) is Decimal  # pylint: disable=unidiomatic-typecheck
    ):
        raise TypeError(f"{field_location} must be a number")

    if max_decimal_places:
        if isinstance(field_value, Decimal):
            if abs(field_value.as_tuple().exponent) > max_decimal_places:
                raise ValueError(
                    f"{field_location} must be a number with a maximum of {max_decimal_places}"
                    + " decimal places"
                )


def get_generic_questionnaire_response_value(
    json_data: dict, link_id: str, field_type: Literal["code", "display", "system"]
) -> Union[str, None]:
    """
    Get the value of a QuestionnaireResponse field, given its linkId
    """

    for record in json_data["contained"]:
        if record["resourceType"] == "QuestionnaireResponse":
            for item in record["item"]:
                if item["linkId"] == link_id:
                    return item["answer"][0]["valueCoding"][field_type]

    raise KeyError(
        "$.contained[?(@.resourceType=='QuestionnaireResponse')]"
        + f".item[?(@.linkId=='{link_id}')].answer[0].valueCoding.{field_type}"
    )


def get_generic_extension_value(
    json_data: dict, url: str, field_type: Literal["code", "display", "system"]
) -> Union[str, None]:
    """
    Get the value of an extension field, given its url
    """

    for record in json_data["extension"]:
        if record["url"] == url:
            return record["valueCodeableConcept"]["coding"][0][field_type]

    raise KeyError(
        f"$.extension[?(@.url=='{url}')].valueCodeableConcept.coding[0].{field_type} does not exist"
    )


def generate_field_location_for_questionnnaire_response(
    link_id: str, field_type: Literal["code", "display", "system"]
) -> str:
    """Generate the field location string for questionnaire response items"""
    return (
        "contained[?(@.resourceType=='QuestionnaireResponse')]"
        + f".item[?(@.linkId=='{link_id}')].answer[0].valueCoding.{field_type}"
    )


def generate_field_location_for_extension(
    url: str, field_type: Literal["code", "display"]
) -> str:
    """Generate the field location string for extension items"""
    return f"extension[?(@.url=='{url}')].valueCodeableConcept.coding[0].{field_type}"
