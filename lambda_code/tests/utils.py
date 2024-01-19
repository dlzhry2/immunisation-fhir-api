"Utils for tests"

import unittest
from copy import deepcopy
from typing import Literal, Any
from decimal import Decimal
from pydantic import ValidationError
from jsonpath_ng.ext import parse


# Lists of data types for 'invalid data type' testing
integers = [-1, 0, 1]
floats = [-1.3, 0.0, 1.0, 2.5]
decimals = [Decimal("-1"), Decimal("0"), Decimal("1"), Decimal("-1.3"), Decimal("2.5")]
booleans = [True, False]
dicts = [{}, {"InvalidKey": "InvalidValue"}]
lists = [[], ["Invalid"]]
strings = ["", "invalid"]


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


def test_valid_values_accepted(
    test_instance: unittest.TestCase,
    valid_json_data: dict,
    field_location: str,
    valid_values_to_test: list,
):
    """Test that valid json data is accepted by the model"""
    for valid_item in valid_values_to_test:
        # Update the value at the relevant field location to the valid value to be tested
        valid_json_data = parse(field_location).update(valid_json_data, valid_item)
        # Test that the valid data is accepted by the model
        test_instance.assertTrue(test_instance.validator.validate(valid_json_data))


def test_invalid_values_rejected(
    test_instance: unittest.TestCase,
    valid_json_data: dict,
    field_location: str,
    invalid_value: Any,
    expected_error_message: str,
    expected_error_type: Literal[
        "type_error", "value_error", "type_error.none.not_allowed"
    ],
):
    """
    Test that invalid json data is rejected by the model, with an appropriate validation error

    NOTE:
    TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
    this happens, the error message is suffixed with the type of error e.g. type_error or
    value_error. This is why the test checks for the type of error in the error message.
    """
    # Create invalid json data by amending the value of the relevant field
    invalid_json_data = parse(field_location).update(valid_json_data, invalid_value)

    # Test that correct error message is raised
    with test_instance.assertRaises(ValidationError) as error:
        test_instance.validator.validate(invalid_json_data)

    test_instance.assertTrue(
        (expected_error_message + f" (type={expected_error_type})")
        in str(error.exception)
    )


def test_missing_mandatory_field_rejected(
    test_instance: unittest.TestCase,
    valid_json_data: dict,
    field_location: str,
    expected_error_message: str,
    expected_error_type: str,
):
    """
    Test that json data which is missing a mandatory field is rejected by the model, with
    an appropriate validation error

    NOTE:
    TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
    this happens, the error message is suffixed with the type of error e.g. type_error or
    value_error. This is why the test checks for the type of error in the error message.
    """

    # Create invalid json data by removing the relevant field
    invalid_json_data = parse(field_location).filter(lambda d: True, valid_json_data)

    # Test that correct error message is raised
    with test_instance.assertRaises(ValidationError) as error:
        test_instance.validator.validate(invalid_json_data)

    test_instance.assertTrue(
        (expected_error_message + f" (type={expected_error_type})")
        in str(error.exception)
    )


class InvalidDataTypes:
    """Store lists of invalid data types for tests"""

    for_integers = [None] + floats + decimals + booleans + dicts + lists + strings
    for_decimals_or_integers = [None] + floats + booleans + dicts + lists + strings
    for_booleans = [None] + integers + floats + decimals + dicts + lists + strings
    for_dicts = [None] + integers + floats + decimals + booleans + lists + strings
    for_lists = [None] + integers + decimals + floats + booleans + dicts + strings
    for_strings = [None] + integers + floats + decimals + booleans + dicts + lists


class ValidValues:
    """Store valid values for tests"""

    for_date_times = [
        "2000-01-01T00:00:00+00:00",  # Time and offset all zeroes
        "1933-12-31T11:11:11+12:45",  # Positive offset (with hours and minutes not 0)
        "1933-12-31T11:11:11-05:00",  # Negative offset
    ]

    # Not a valid snomed code, but is valid coding format for format testing
    snomed_coding_element = {
        "system": "http://snomed.info/sct",
        "code": "ABC123",
        "display": "test",
    }


class InvalidValues:
    """Store lists of invalid values for tests"""

    for_postal_codes = [
        "SW1  1AA",  # Too many spaces in divider
        "SW 1 1A",  # Too many space dividers
        "AAA0000AA",  # Too few space dividers
        " AA00 00AA",  # Invalid additional space at start
        "AA00 00AA ",  # Invalid additional space at end
        " AA0000AA",  # Space is incorrectly at start
        "AA0000AA ",  # Space is incorrectly at end
    ]

    for_date_string_formats = [
        # Strings which are not in acceptable date format
        "",  # Empty
        "invalid",  # With letters
        "20000101",  # Without dashes
        "200001-01",  # Missing first dash
        "2000-0101",  # Missing second dash
        "2000:01:01",  # Semi-colons instead of dashes
        "2000-01-011",  # Extra digit at end
        "12000-01-01",  # Extra digit at start
        "12000-01-021",  # Extra digit at start and end
        "99-01-01",  # Year represented without century (i.e. 2 digits instead of 4)
        "01-01-1999",  # DD-MM-YYYY format
        "01-01-99",  # DD-MM-YY format
        # Strings which are in acceptable date format, but are invalid dates
        "2000-00-01",  # Month 0
        "2000-13-01",  # Month 13
        "2000-01-00",  # Day 0
        "2000-01-32",  # Day 32
        "2000-02-30",  # Invalid combnation of month and day
    ]

    # Strings which are not in acceptable date time format
    for_date_time_string_formats = [
        "",  # Empty string
        "invalid",  # Invalid format
        "20000101",  # Date digits only (i.e. without hypens)
        "20000101000000",  # Date and time digits only
        "200001010000000000",  # Date, time and timezone digits only
        "2000-01-01",  # Date only
        "2000-01-01T00:00:00",  # Date and time only
        "2000-01-01T00:00:00+00",  # Date and time with GMT timezone offset only in hours
        "2000-01-01T00:00:00+01",  # Date and time with BST timezone offset only in hours
        "12000-01-01T00:00:00+00:00",  # Extra character at start of string
        "2000-01-01T00:00:00+00:001",  # Extra character at end of string
        "12000-01-02T00:00:00-01:001",  # Extra characters at start and end of string
        "2000-01-0122:22:22+00:00",  # Missing T
        "2000-01-01T222222+00:00",  # Missing time colons
        "2000-01-01T22:22:2200:00",  # Missing timezone indicator
        "2000-01-01T22:22:22-0100",  # Missing timezone colon
        "99-01-01T00:00:00+00:00",  # Missing century (i.e. only 2 digits for year)
        "01-01-2000T00:00:00+00:00",  # Date in wrong order (DD-MM-YYYY)
    ]

    # Strings which are in acceptable date time format, but are invalid dates, times or timezones
    for_date_times = [
        "2000-00-01T00:00:00+00:00",  # Month 00
        "2000-13-01T00:00:00+00:00",  # Month 13
        "2000-01-00T00:00:00+00:00",  # Day 00
        "2000-01-32T00:00:00+00:00",  # Day 32
        "2000-02-30T00:00:00+00:00",  # Invalid month and day combination (30th February)
        "2000-01-01T24:00:00+00:00",  # Hour 24
        "2000-01-01T00:60:00+00:00",  # Minute 60
        "2000-01-01T00:00:60+00:00",  # Second 60
        "2000-01-01T00:00:00+24:00",  # Timezone hour +24
        "2000-01-01T00:00:00-24:00",  # Timezone hour -24
        "2000-01-01T00:00:00+00:60",  # Timezone minute 60
    ]

    for_lists_of_strings_of_length_1 = [[1], [False], [["Test1"]]]

    for_strings_with_max_100_chars = [
        "This is a really long string with more than 100 "
        + "characters to test whether the validator is working well"
    ]


class ValidatorModelTests:
    """Generic tests for model validators"""

    @staticmethod
    def test_string_value(
        test_instance: unittest.TestCase,
        field_location: str,
        valid_strings_to_test: dict,
        defined_length: int = None,
        max_length: int = None,
        invalid_length_strings_to_test: list = None,
        predefined_values: tuple = None,
        invalid_strings_to_test: list = None,
        spaces_allowed: bool = True,
        invalid_strings_with_spaces_to_test: list = None,
        is_postal_code: bool = False,
        is_mandatory_fhir: bool = False,
    ):
        """
        Test that a FHIR model accepts valid string values and rejects the following invalid values:
        * All invalid data types
        * If there is a defined_string_length: Strings of invalid length (defined by the argument
            invalid_length_strings_to_test), plus the empty string
        * If there is no defined_string_length: Empty strings
        * If there is a max_length: Strings longer than max length (defined by the argument
            invalid_length_strings_to_test)
        * If there are predefined values: Invalid strings (i.e. not one of the predefined values) as
            defined by the argument invalid_strings_to_test
        * If the field is manadatory in FHIR: Value of None
        * If spaces are not allowed: Strings with spaces, which would be valid without the
            spaces (defined by the argument invalid_strings_with_spaces_to_test)
        * If is a postal code: Postal codes which are not separated into two parts by a single
            space, or which exceed the maximum length of 8 characters (excluding spaces)

        NOTE: No validation of optional arguments will occur if the method is not given a list of
        values to test. This means that:
        * When optional arguments defined_length and max_length are given, the optional argument
            invalid_length_strings_to_test MUST also be given
        * When optional argument predefined_values is given, the optional argument
            invalid_strings_to_test MUST also be given.
        * When optional argument spaces_allowed is given, the optional argument
            invalid_strings_with_spaces_test must also be given
        """

        valid_json_data = deepcopy(test_instance.json_data)

        # Test that valid data is accepted
        test_valid_values_accepted(
            test_instance, valid_json_data, field_location, valid_strings_to_test
        )

        # If is mandatory FHIR, then for none type the model raises an
        # exception prior to running NHS pre-validators
        if is_mandatory_fhir:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=None,
                expected_error_message="none is not an allowed value",
                expected_error_type="type_error.none.not_allowed",
            )

        # Set list of invalid data types to test
        invalid_data_types_for_strings = InvalidDataTypes.for_strings
        if is_mandatory_fhir:
            invalid_data_types_for_strings = filter(
                None, invalid_data_types_for_strings
            )

        # Test invalid data types
        for invalid_data_type_for_string in invalid_data_types_for_strings:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_data_type_for_string,
                expected_error_message=f"{field_location} must be a string",
                expected_error_type="type_error",
            )

        # If there is a predefined string length, then test invalid string lengths,
        # otherwise check the empty string only
        if defined_length:
            for invalid_length_string in invalid_length_strings_to_test:
                test_invalid_values_rejected(
                    test_instance,
                    valid_json_data,
                    field_location=field_location,
                    invalid_value=invalid_length_string,
                    expected_error_message=f"{field_location} must be {defined_length} characters",
                    expected_error_type="value_error",
                )
        else:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value="",
                expected_error_message=f"{field_location} must be a non-empty string",
                expected_error_type="value_error",
            )

        # If there is a max_length, test strings which exceed that length
        if max_length:
            for invalid_length_string in invalid_length_strings_to_test:
                test_invalid_values_rejected(
                    test_instance,
                    valid_json_data,
                    field_location=field_location,
                    invalid_value=invalid_length_string,
                    expected_error_message=f"{field_location} must be {max_length} "
                    + "or fewer characters",
                    expected_error_type="value_error",
                )

        # If there are predefined values, then test strings which are
        # not in the set of predefined values
        if predefined_values:
            for invalid_string in invalid_strings_to_test:
                test_invalid_values_rejected(
                    test_instance,
                    valid_json_data,
                    field_location=field_location,
                    invalid_value=invalid_string,
                    expected_error_message=f"{field_location} must be one of the following: "
                    + str(", ".join(predefined_values)),
                    expected_error_type="value_error",
                )

        # If spaces are not allowed, then test strings with spaces
        if not spaces_allowed:
            for invalid_string_with_spaces in invalid_strings_with_spaces_to_test:
                test_invalid_values_rejected(
                    test_instance,
                    valid_json_data,
                    field_location=field_location,
                    invalid_value=invalid_string_with_spaces,
                    expected_error_message=f"{field_location} must not contain spaces",
                    expected_error_type="value_error",
                )

        # If is a postal code, then test postal codes which are not separated into the two parts
        # by a single space or which exceed the maximum length of 8 characters (excluding spaces)
        if is_postal_code:
            # Test postal codes which are not separated into the two parts by a single space
            for invalid_postal_code in InvalidValues.for_postal_codes:
                test_invalid_values_rejected(
                    test_instance,
                    valid_json_data,
                    field_location=field_location,
                    invalid_value=invalid_postal_code,
                    expected_error_message=f"{field_location} must contain a single space, "
                    + "which divides the two parts of the postal code",
                    expected_error_type="value_error",
                )

            # Test invalid postal code length
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value="AA000 00AA",
                expected_error_message=f"{field_location} must be 8 or fewer characters "
                + "(excluding spaces)",
                expected_error_type="value_error",
            )

    @staticmethod
    def test_list_value(
        test_instance: unittest.TestCase,
        field_location: str,
        valid_lists_to_test: list,
        predefined_list_length: int = None,
        valid_list_element=None,
        is_list_of_strings: bool = False,
    ):
        """
        Test that a FHIR model accepts valid list values and rejects the following invalid values:
        * All invalid data types
        * If there is a predefined list length: Strings of invalid length, plus the empty list (note
            that a valid list element must be supplied when a predefined list length is given as
            the valid element will be used to populate lists of incorrect length to ensure
            that the error is being raised due to length, not due to use of an invalid list element)
        * If there is no predfined list length: Empty list
        * If is a list of strings: Lists with non-string or empty string elements

        NOTE: No validation of optional arguments will occur if the method is not given a list of
        values to test. This means that:
        * When optional arguments predefined_list_length is given, the optional argument
            invalid_length_lists_to_test MUST also be given
        """

        valid_json_data = deepcopy(test_instance.json_data)

        # Test that valid data is accepted
        test_valid_values_accepted(
            test_instance, valid_json_data, field_location, valid_lists_to_test
        )

        # Test invalid data types
        for invalid_data_type_for_list in InvalidDataTypes.for_lists:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_data_type_for_list,
                expected_error_message=f"{field_location} must be an array",
                expected_error_type="type_error",
            )

        # If there is a predefined list length, then test the empty list and a list which is
        # larger than the predefined length, otherwise check the empty list only
        if predefined_list_length:
            # Set up list of invalid_length_lists
            list_too_short = []
            for _ in range(predefined_list_length - 1):
                list_too_short.append(valid_list_element)

            list_too_long = []
            for _ in range(predefined_list_length + 1):
                list_too_long.append(valid_list_element)

            invalid_length_lists = [list_too_short, list_too_long]

            if predefined_list_length != 1:  # If is 1 then list_too_short = []
                invalid_length_lists.append([])

            # Test invalid list lengths
            for invalid_length_list in invalid_length_lists:
                test_invalid_values_rejected(
                    test_instance,
                    valid_json_data,
                    field_location=field_location,
                    invalid_value=invalid_length_list,
                    expected_error_message=f"{field_location} must be an array of length "
                    + f"{predefined_list_length}",
                    expected_error_type="value_error",
                )
        else:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=[],
                expected_error_message=f"{field_location} must be a non-empty array",
                expected_error_type="value_error",
            )

        # Tests lists with non-string or empty string elements (if applicable)
        if is_list_of_strings:
            # Test lists with non-string element
            for invalid_list in InvalidValues.for_lists_of_strings_of_length_1:
                test_invalid_values_rejected(
                    test_instance,
                    valid_json_data,
                    field_location=field_location,
                    invalid_value=invalid_list,
                    expected_error_message=f"{field_location} must be an array of strings",
                    expected_error_type="type_error",
                )

            # Test empty string in list
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=[""],
                expected_error_message=f"{field_location} must be an array of non-empty strings",
                expected_error_type="value_error",
            )

    @staticmethod
    def test_date_value(
        test_instance: unittest.TestCase,
        field_location: str,
    ):
        """
        Test that a FHIR model accepts valid date values and rejects the following invalid values:
        * All invalid data types
        * Invalid date formats
        * Invalid dates
        """

        valid_json_data = deepcopy(test_instance.json_data)

        # Test that valid data is accepted
        test_valid_values_accepted(
            test_instance, valid_json_data, field_location, ["2000-01-01", "1933-12-31"]
        )

        # Test invalid data types
        for invalid_data_type_for_string in InvalidDataTypes.for_strings:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_data_type_for_string,
                expected_error_message=f"{field_location} must be a string",
                expected_error_type="type_error",
            )

        # Test invalid date string formats
        for invalid_date_format in InvalidValues.for_date_string_formats:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_date_format,
                expected_error_message=f"{field_location} must be a valid date string in the "
                + 'format "YYYY-MM-DD"',
                expected_error_type="value_error",
            )

    @staticmethod
    def test_date_time_value(
        test_instance: unittest.TestCase,
        field_location: str,
        is_occurrence_date_time: bool = False,
    ):
        """
        Test that a FHIR model accepts valid date-time values and rejects the following invalid
        values:
        * All invalid data types
        * Invalid date time string formats
        * Invalid date-times
        """

        valid_json_data = deepcopy(test_instance.json_data)

        # Test that valid data is accepted
        test_valid_values_accepted(
            test_instance, valid_json_data, field_location, ValidValues.for_date_times
        )

        # If is occurrenceDateTime, then for none type the model raises an exception prior to
        # running NHS pre-validators, because occurrenceDateTime is a mandatory FHIR field
        if is_occurrence_date_time:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=None,
                expected_error_message="Expect any of field value from this list "
                + "['occurrenceDateTime', 'occurrenceString'].",
                expected_error_type="value_error",
            )

        # Set list of invalid data types to test
        invalid_data_types_for_strings = InvalidDataTypes.for_strings
        if is_occurrence_date_time:
            invalid_data_types_for_strings = filter(
                None, invalid_data_types_for_strings
            )

        # Test invalid data types
        for invalid_data_type_for_string in invalid_data_types_for_strings:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_data_type_for_string,
                expected_error_message=f"{field_location} must be a string",
                expected_error_type="type_error",
            )

        # Test invalid date time string formats
        for invalid_occurrence_date_time in InvalidValues.for_date_time_string_formats:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_occurrence_date_time,
                expected_error_message=f"{field_location} must be a string in the format "
                + '"YYYY-MM-DDThh:mm:ss+zz:zz" or"YYYY-MM-DDThh:mm:ss-zz:zz" (i.e date and time, '
                + "including timezone offset in hours and minutes)",
                expected_error_type="value_error",
            )

        # Test invalid date times
        for invalid_occurrence_date_time in InvalidValues.for_date_times:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_occurrence_date_time,
                expected_error_message=f"{field_location} must be a valid datetime",
                expected_error_type="value_error",
            )

    @staticmethod
    def test_boolean_value(
        test_instance: unittest.TestCase,
        field_location: str,
    ):
        """Test that a FHIR model accepts valid boolean values and rejects non-boolean values."""

        valid_json_data = deepcopy(test_instance.json_data)

        # Test that valid data is accepted
        test_valid_values_accepted(
            test_instance, valid_json_data, field_location, [True, False]
        )

        # Test invalid data types
        for invalid_data_type_for_boolean in InvalidDataTypes.for_booleans:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_data_type_for_boolean,
                expected_error_message=f"{field_location} must be a boolean",
                expected_error_type="type_error",
            )

    @staticmethod
    def test_positive_integer_value(
        test_instance: unittest.TestCase,
        field_location: str,
        valid_positive_integers_to_test: list,
        max_value: int = None,
    ):
        """
        Test that a FHIR model accepts valid positive integer values and rejects the following
        invalid values:
        * All invalid data types
        * Non-postive integers
        * If there is a max value: a value which exceeds the maximum
        """

        valid_json_data = deepcopy(test_instance.json_data)

        # Test that valid data is accepted
        test_valid_values_accepted(
            test_instance,
            valid_json_data,
            field_location,
            valid_positive_integers_to_test,
        )

        # Test invalid data types
        for invalid_data_type_for_integer in InvalidDataTypes.for_integers:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_data_type_for_integer,
                expected_error_message=f"{field_location} must be a positive integer",
                expected_error_type="type_error",
            )

        # Test non-positive integers
        for non_positive_integer in [-10, -1, 0]:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=non_positive_integer,
                expected_error_message=f"{field_location} must be a positive integer",
                expected_error_type="value_error",
            )

        # Test value exceeding the max value (if applicable)
        if max_value:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=max_value + 1,
                expected_error_message=f"{field_location} must be an integer in the range 1 to "
                + f"{str(max_value)}",
                expected_error_type="value_error",
            )

    @staticmethod
    def test_decimal_or_integer_value(
        test_instance: unittest.TestCase,
        field_location: str,
        valid_decimals_and_integers_to_test: list,
        max_decimal_places: int = None,
    ):
        """
        Test that a FHIR model accepts valid decimal or integer values and rejects the following
        invalid values:
        * All invalid data types
        * If there is a max number of decimal places: a Decimal with too many decimal places
        """

        valid_json_data = deepcopy(test_instance.json_data)

        # Test that valid data is accepted
        test_valid_values_accepted(
            test_instance,
            valid_json_data,
            field_location,
            valid_decimals_and_integers_to_test,
        )

        # Test invalid data types
        for (
            invalid_data_type_for_decimals_or_integers
        ) in InvalidDataTypes.for_decimals_or_integers:
            test_invalid_values_rejected(
                test_instance,
                valid_json_data,
                field_location=field_location,
                invalid_value=invalid_data_type_for_decimals_or_integers,
                expected_error_message=f"{field_location} must be a number",
                expected_error_type="type_error",
            )

        # Test Decimal with more than the maximum number of decimal places
        decimal_too_many_dp = Decimal("1." + "1" * (max_decimal_places + 1))
        test_invalid_values_rejected(
            test_instance,
            valid_json_data,
            field_location=field_location,
            invalid_value=decimal_too_many_dp,
            expected_error_message=f"{field_location} must be a number with a maximum of "
            + f"{max_decimal_places} decimal places",
            expected_error_type="value_error",
        )
