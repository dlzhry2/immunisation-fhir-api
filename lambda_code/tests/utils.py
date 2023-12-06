"Utils for tests"

from typing import Callable, Literal
import unittest


def generate_field_location_for_questionnnaire_response(
    link_id: str, field_type: Literal["code", "display", "system"]
) -> str:
    """Generate the field location string for questionnaire response items"""
    return (
        "contained[0] -> resourceType[QuestionnaireResponse]: "
        + f"item[*] -> linkId[{link_id}]: answer[0] -> valueCoding -> {field_type}"
    )


class InvalidDataTypes:
    """ "Store lists of  invalid data types for tests"""

    for_strings = [
        None,
        -1,
        0,
        0.0,
        1,
        True,
        {},
        [],
        (),
        {"InvalidKey": "InvalidValue"},
        ["Invalid"],
        ("Invalid1", "Invalid2"),
    ]

    for_lists = [
        None,
        -1,
        0,
        0.0,
        1,
        True,
        {},
        "",
        {"InvalidKey": "InvalidValue"},
        "Invalid",
    ]

    for_dicts = [
        None,
        -1,
        0,
        0.0,
        1,
        True,
        [],
        "",
        ["Invalid"],
        "Invalid",
    ]

    for_booleans = [
        None,
        -1,
        0,
        0.0,
        1,
        "",
        {},
        [],
        (),
        "Invalid",
        {"InvalidKey": "InvalidValue"},
        ["Invalid"],
        ("Invalid1", "Invalid2"),
    ]

    for_integers = [
        None,
        True,
        "",
        {},
        [],
        (),
        "Invalid",
        {"InvalidKey": "InvalidValue"},
        ["Invalid"],
        ("Invalid1", "Invalid2"),
    ]


class GenericValidatorMethodTests:
    """Generic tests for method validators"""

    @staticmethod
    def valid(
        test_instance: unittest.TestCase,
        validator: Callable,
        valid_items_to_test: list,
    ):
        """Test that a validator method accepts valid strings"""
        for valid_item in valid_items_to_test:
            test_instance.assertEqual(validator(valid_item), valid_item)

    @staticmethod
    def string_invalid(
        test_instance: unittest.TestCase,
        validator: Callable,
        field_location: str,
        defined_length: int = None,
        invalid_length_strings_to_test: list = None,
        predefined_values: tuple = None,
        invalid_strings_to_test: list = None,
    ):
        """
        Test that a validator method rejects the following invalid strings:
        * All invalid data types
        * If there is a predefined string length: Strings of invalid length (defined by the argument
            invalid_length_strings_to_test - this should include an empty string)
        * If there is no predfined string length: Empty strings
        * If there are predefined values: Invalid strings (i.e. not one of the predefined values)
        """
        # Test invalid data types
        for invalid_data_type_for_string in InvalidDataTypes.for_strings:
            with test_instance.assertRaises(TypeError) as error:
                validator(invalid_data_type_for_string)

            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a string",
            )

        # If there is a predefined string length, then test invalid string lengths,
        # otherwise check the empty string only
        if defined_length:
            for invalid_length_string in invalid_length_strings_to_test:
                with test_instance.assertRaises(ValueError) as error:
                    validator(invalid_length_string)

                test_instance.assertEqual(
                    str(error.exception),
                    f"{field_location} must be {defined_length} characters",
                )
        else:
            with test_instance.assertRaises(ValueError) as error:
                validator("")
            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a non-empty string",
            )

        if predefined_values:
            for invalid_string in invalid_strings_to_test:
                with test_instance.assertRaises(ValueError) as error:
                    validator(invalid_string)
                test_instance.assertEqual(
                    str(error.exception),
                    f"{field_location} must be one of the following: "
                    + str(", ".join(predefined_values)),
                )

    @staticmethod
    def list_invalid(
        test_instance: unittest.TestCase,
        validator: Callable,
        field_location: str,
        predefined_list_length: int = None,
        invalid_length_lists_to_test: list = None,
        invalid_lists_with_non_string_data_types_to_test: list = None,
    ):
        """
        Test that a validator method rejects the following invalid lists:
        * All invalid data types
        * If there is a predefined list length: Strings of invalid length (defined by the argument
            invalid_length_lists_to_test - this should include an empty list)
        * If there is no predfined list length: Empty lists
        * If there is a list of invalid_lists_with_non_string_data_types_to_test: Each of the
            items in the list, plus a
        """
        # Test invalid data types
        for invalid_data_type_for_list in InvalidDataTypes.for_lists:
            with test_instance.assertRaises(TypeError) as error:
                validator(invalid_data_type_for_list)

            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be an array",
            )

        # If there is a predefined list length, then test invalid list lengths,
        # otherwise check the empty list only
        if predefined_list_length:
            for invalid_length_list in invalid_length_lists_to_test:
                with test_instance.assertRaises(ValueError) as error:
                    validator(invalid_length_list)

                test_instance.assertEqual(
                    str(error.exception),
                    f"{field_location} must be an array of length {predefined_list_length}",
                )
        else:
            with test_instance.assertRaises(ValueError) as error:
                validator([])
            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a non-empty array",
            )

        # Tests invalid_lists_with_non_string_data_types_to_test (if provided)
        if invalid_lists_with_non_string_data_types_to_test:
            # Test each invalid list
            for invalid_list in invalid_lists_with_non_string_data_types_to_test:
                with test_instance.assertRaises(TypeError) as error:
                    validator(invalid_list)

                test_instance.assertEqual(
                    str(error.exception),
                    f"{field_location} must be an array of strings",
                )

            # Test empty string in list
            with test_instance.assertRaises(ValueError) as error:
                validator([""])
            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be an array of non-empty strings",
            )

    @staticmethod
    def date_invalid(
        test_instance: unittest.TestCase, validator: Callable, field_location: str
    ):
        """
        Test that a validator method rejects the following:
        * All invalid data types
        * Invalid date formats
        * Invalid dates
        """
        # Test invalid data types
        for invalid_data_type_for_string in InvalidDataTypes.for_strings:
            with test_instance.assertRaises(TypeError) as error:
                validator(invalid_data_type_for_string)

            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a string",
            )

        # Test invalid date string formats
        invalid_date_formats = [
            "",  # Empty
            "invalid",  # With letters
            "20000101",  # Without dashes
            "2000-01-011",  # Extra digit at end
            "12000-01-01",  # Extra digit at start
            "12000-01-021",  # Extra digit at start and end
            "99-01-01",  # Year represented without century (i.e. 2 digits instead of 4)
            "01-01-1999",  # DD-MM-YYYY format
            "01-01-99",  # DD-MM-YY format
        ]
        for invalid_date_format in invalid_date_formats:
            with test_instance.assertRaises(ValueError) as error:
                validator(invalid_date_format)
            test_instance.assertEqual(
                str(error.exception),
                f'{field_location} must be a string in the format "YYYY-MM-DD"',
            )

        # Test invalid dates
        invalid_dates = [
            "2000-00-01",  # Month 0
            "2000-13-01",  # Month 13
            "2000-01-00",  # Day 0
            "2000-01-32",  # Day 13
            "2000-02-30",  # Invalid combnation of month and day
        ]
        for invalid_date in invalid_dates:
            with test_instance.assertRaises(ValueError) as error:
                validator(invalid_date)
            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a valid date",
            )
