"""Generic utilities for models"""

import re
from datetime import datetime


def generic_string_validation(
    field_value: str,
    field_location: str,
    defined_length: int = 0,
    max_length: int = 0,
    predefined_values: set = None,
):
    """
    Apply generic validation to a string field to ensure it is a non-empty string which meets
    the length requirements
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


def generic_list_validation(
    field_value: list, field_location: str, defined_length: int = 0
):
    """
    Apply generic validation to a list field to ensure it is a non-empty list which meets
    the length requirements
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


def generic_date_validation(field_value: str, field_location: str):
    if not isinstance(field_value, str):
        raise TypeError(f"{field_location} must be a string")

    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

    if not date_pattern.fullmatch(field_value):
        raise ValueError(
            f'{field_location} must be a string in the format "YYYY-MM-DD"'
        )

    try:
        datetime.strptime(field_value, "%Y-%m-%d").date()
    except ValueError as value_error:
        raise ValueError(f"{field_location} must be a valid date") from value_error
