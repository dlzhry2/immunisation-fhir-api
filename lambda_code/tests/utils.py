"Utils for tests"

import unittest
from copy import deepcopy
from typing import Literal
from decimal import Decimal
from pydantic import ValidationError
from jsonpath_ng.ext import parse


def generate_field_location_for_questionnnaire_response(
    link_id: str, field_type: Literal["code", "display", "system"]
) -> str:
    """Generate the field location string for questionnaire response items"""
    return (
        "contained[?(@.resourceType=='QuestionnaireResponse')]"
        + f".item[?(@.linkId=='{link_id}')].answer[0].valueCoding.{field_type}"
    )


def generate_field_location_for_extension(
    url: str, field_type: Literal["code", "display", "system"]
) -> str:
    """Generate the field location string for extension items"""
    return f"extension[?(@.url=='{url}')].valueCodeableConcept.coding[0].{field_type}"


class InvalidDataTypes:
    """Store lists of invalid data types for tests"""

    integers = [-1, 0, 1]
    floats = [-1.3, 0.0, 1.0, 2.5]
    decimals = [Decimal(-1), Decimal(0), Decimal(1), Decimal(-1.3), Decimal(2.5)]
    booleans = [True, False]
    dicts = [{}, {"InvalidKey": "InvalidValue"}]
    lists = [[], ["Invalid"]]
    strings = ["", "invalid"]

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
        "2000-01-32",  # Day 13
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
    """
    Generic tests for model validators

    NOTE:
    TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
    this happens, the error message is suffixed with the type of error e.g. type_error or
    value_error. This is why the tests check for the type of error in the error message.
    """

    @staticmethod
    def valid(
        test_instance: unittest.TestCase,
        field_location,
        valid_items_to_test: list,
    ):
        """Test that a validator method accepts valid data when in a model"""
        valid_json_data = deepcopy(test_instance.json_data)

        for valid_item in valid_items_to_test:
            valid_json_data = parse(field_location).update(valid_json_data, valid_item)

            test_instance.assertTrue(test_instance.validator.validate(valid_json_data))

    @staticmethod
    def string_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
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
        Test that a validator rejects the following invalid strings when in a model:
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

        NOTE: No validation of optional arguments will occur if the method is not given a list of
        values to test. This means that:
        * When optional arguments defined_length and max_length are given, the optional argument
            invalid_length_strings_to_test MUST also be given
        * When optional argument predefined_lines is given, the optional argument
            invalid_strings_to_test MUST also be given.
        * When optional argument spaces_allowed is given, the optional argument
            invalid_strings_with_spaces_test must also be given
        """

        invalid_json_data = deepcopy(test_instance.json_data)

        # If is mandatory FHIR, then for none type the model raises an
        # exception prior to running NHS pre-validators
        if is_mandatory_fhir:
            invalid_json_data = parse(field_location).update(invalid_json_data, None)
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                "none is not an allowed value (type=type_error.none.not_allowed)"
                in str(error.exception)
            )

        # Set list of invalid data types to test
        invalid_data_types_for_strings = InvalidDataTypes.for_strings
        if is_mandatory_fhir:
            invalid_data_types_for_strings = filter(
                None, invalid_data_types_for_strings
            )

        # Test invalid data types
        for invalid_data_type_for_string in invalid_data_types_for_strings:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_data_type_for_string
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a string (type=type_error)"
                in str(error.exception)
            )

        # If there is a predefined string length, then test invalid string lengths,
        # otherwise check the empty string only
        if defined_length:
            for invalid_length_string in invalid_length_strings_to_test:
                invalid_json_data = parse(field_location).update(
                    invalid_json_data, invalid_length_string
                )
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be 10 characters (type=value_error)"
                    in str(error.exception)
                )
        else:
            invalid_json_data = parse(field_location).update(invalid_json_data, "")
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a non-empty string (type=value_error)"
                in str(error.exception)
            )

        # If there is a max_length, test strings which exceed that length
        if max_length:
            for invalid_length_string in invalid_length_strings_to_test:
                invalid_json_data = parse(field_location).update(
                    invalid_json_data, invalid_length_string
                )
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be {max_length} or fewer characters (type=value_error)"
                    in str(error.exception)
                )

        # If there are predefined values, then test strings which are
        # not in the set of predefined values
        if predefined_values:
            for invalid_string in invalid_strings_to_test:
                invalid_json_data = parse(field_location).update(
                    invalid_json_data, invalid_string
                )
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be one of the following: "
                    + str(", ".join(predefined_values))
                    + " (type=value_error)"
                    in str(error.exception)
                )

        # If spaces are not allowed, then test strings with spaces
        if not spaces_allowed:
            invalid_json_data = deepcopy(test_instance.json_data)

            for invalid_string_with_spaces in invalid_strings_with_spaces_to_test:
                invalid_json_data = parse(field_location).update(
                    invalid_json_data, invalid_string_with_spaces
                )
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must not contain spaces (type=value_error)"
                    in str(error.exception)
                )

        # If is a postal code, then test postal codes which are not separated into the two parts
        # by a single space or which exceed the maximum length of 8 characters (excluding spaces)
        if is_postal_code:
            invalid_json_data = deepcopy(test_instance.json_data)

            # Test postal codes which are not separated into the two parts by a single space
            for invalid_postal_code in InvalidValues.for_postal_codes:
                invalid_json_data = parse(field_location).update(
                    invalid_json_data, invalid_postal_code
                )

                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must contain a single space, "
                    + "which divides the two parts of the postal code (type=value_error)"
                    in str(error.exception)
                )

            # Test invalid postal code length
            invalid_json_data = parse("address[0].postalCode").update(
                invalid_json_data, "AA000 00AA"
            )

            # Check that we get the correct error message and that it contains type=value_error
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be 8 or fewer characters "
                + "(excluding spaces) (type=value_error)"
                in str(error.exception)
            )

    @staticmethod
    def list_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
        predefined_list_length: int = None,
        valid_list_element=None,
        is_list_of_strings: bool = False,
    ):
        """
        Test that a validator rejects the following invalid lists when in a model:
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

        invalid_json_data = deepcopy(test_instance.json_data)

        # Test invalid data types
        for invalid_data_type_for_list in InvalidDataTypes.for_lists:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_data_type_for_list
            )

            # Check that we get the correct error message and that it contains type=value_error
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be an array (type=type_error)"
                in str(error.exception)
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

            if predefined_list_length is not 1:  # If is 1 then list_too_short = []
                invalid_length_lists.append([])

            # Test invalid list lengths
            for invalid_length_list in invalid_length_lists:
                invalid_json_data = parse(field_location).update(
                    invalid_json_data, invalid_length_list
                )
                with test_instance.assertRaises(ValueError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be an array of length {predefined_list_length}"
                    + " (type=value_error)"
                    in str(error.exception)
                )
        else:
            invalid_json_data = parse(field_location).update(invalid_json_data, [])
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a non-empty array (type=value_error)"
                in str(error.exception)
            )

        # Tests lists with non-string or empty string elements (if applicable)
        if is_list_of_strings:
            # Test lists with non-string element
            for invalid_list in InvalidValues.for_lists_of_strings_of_length_1:
                invalid_json_data = parse(field_location).update(
                    invalid_json_data, invalid_list
                )
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be an array of strings (type=type_error)"
                    in str(error.exception)
                )

            # Test empty string in list
            invalid_json_data = parse(field_location).update(invalid_json_data, [""])
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be an array of non-empty strings (type=value_error)"
                in str(error.exception)
            )

    @staticmethod
    def date_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
    ):
        """
        Test that a validator method rejects the following when in a model:
        * All invalid data types
        * Invalid date formats
        * Invalid dates
        """

        invalid_json_data = deepcopy(test_instance.json_data)

        # Test invalid data types
        for invalid_data_type_for_string in InvalidDataTypes.for_strings:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_data_type_for_string
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a string (type=type_error)"
                in str(error.exception)
            )

        # Test invalid date string formats
        for invalid_date_format in InvalidValues.for_date_string_formats:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_date_format
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f'{field_location} must be a valid date string in the format "YYYY-MM-DD" '
                + "(type=value_error)"
                in str(error.exception)
            )

    @staticmethod
    def date_time_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
        is_occurrence_date_time: bool = False,
    ):
        """
        Test that a validator method rejects the following when in a model:
        * All invalid data types
        * Invalid date time string formats
        * Invalid date-times
        """

        invalid_json_data = deepcopy(test_instance.json_data)

        # If is occurrenceDateTime, then for none type the model raises an exception prior to
        # running NHS pre-validators, because occurrenceDateTime is a mandatory FHIR field
        if is_occurrence_date_time:
            invalid_json_data = parse(field_location).update(invalid_json_data, None)

            # Check that we get the correct error message and that it contains type=type_error
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                "Expect any of field value from this list "
                + "['occurrenceDateTime', 'occurrenceString']. (type=value_error)"
                in str(error.exception)
            )

        # Set list of invalid data types to test
        invalid_data_types_for_strings = InvalidDataTypes.for_strings
        if is_occurrence_date_time:
            invalid_data_types_for_strings = filter(
                None, invalid_data_types_for_strings
            )

        # Test invalid data types
        for invalid_data_type_for_string in invalid_data_types_for_strings:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_data_type_for_string
            )
            # Check that we get the correct error message and that it contains type=type_error
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a string (type=type_error)"
                in str(error.exception)
            )

        # Test invalid date time string formats
        for invalid_occurrence_date_time in InvalidValues.for_date_time_string_formats:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_occurrence_date_time
            )
            # Check that we get the correct error message and that it contains type=value_error
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f'{field_location} must be a string in the format "YYYY-MM-DDThh:mm:ss+zz:zz" or'
                + '"YYYY-MM-DDThh:mm:ss-zz:zz" (i.e date and time, including timezone offset in '
                + "hours and minutes)"
                in str(error.exception)
            )

        # Test invalid date times
        for invalid_occurrence_date_time in InvalidValues.for_date_times:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_occurrence_date_time
            )
            # Check that we get the correct error message and that it contains type=value_error
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a valid datetime (type=value_error)"
                in str(error.exception)
            )

    @staticmethod
    def boolean_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
    ):
        """Test that a validator rejects any non-boolean value when in a model"""

        invalid_json_data = deepcopy(test_instance.json_data)

        # Test invalid data types
        for invalid_data_type_for_boolean in InvalidDataTypes.for_booleans:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_data_type_for_boolean
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a boolean (type=type_error)"
                in str(error.exception)
            )

    @staticmethod
    def positive_integer_invalid(
        test_instance: unittest.TestCase, field_location: str, max_value: int = None
    ):
        """
        Test that a validator method rejects the following when in a model:
        * All invalid data types
        * Non-postive integers
        * If there is a max value: a value which exceeds the maximum
        """

        invalid_json_data = deepcopy(test_instance.json_data)

        # Test invalid data types
        for invalid_data_type_for_integer in InvalidDataTypes.for_integers:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_data_type_for_integer
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a positive integer (type=type_error)"
                in str(error.exception)
            )

        # Test non-positive integers
        for non_positive_integer in [-10, -1, 0]:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, non_positive_integer
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a positive integer (type=value_error)"
                in str(error.exception)
            )

        # Test value exceeding the max value (if applicable)
        if max_value:
            invalid_json_data = deepcopy(test_instance.json_data)

            invalid_json_data = parse(field_location).update(
                invalid_json_data, max_value + 1
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be an integer in the range 1 to {str(max_value)}"
                + " (type=value_error)"
                in str(error.exception)
            )

    @staticmethod
    def decimal_or_integer_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
        max_decimal_places: int = None,
    ):
        """
        Test that a validator method rejects the following when in a model:
        * All invalid data types
        * If there is a max number of decimal places: a Decimal with too many decimal places
        """

        invalid_json_data = deepcopy(test_instance.json_data)

        # Test invalid data types
        for invalid_data_type in InvalidDataTypes.for_decimals_or_integers:
            invalid_json_data = parse(field_location).update(
                invalid_json_data, invalid_data_type
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a number (type=type_error)"
                in str(error.exception)
            )

        # Test Decimal with more than the maximum number of decimal places
        decimal_too_many_dp = Decimal("1." + "1" * (max_decimal_places + 1))
        invalid_json_data = parse(field_location).update(
            invalid_json_data, decimal_too_many_dp
        )

        with test_instance.assertRaises(ValidationError) as error:
            test_instance.validator.validate(invalid_json_data)

        test_instance.assertTrue(
            f"{field_location} must be a number with a maximum of {max_decimal_places}"
            + " decimal places (type=value_error)"
            in str(error.exception)
        )
