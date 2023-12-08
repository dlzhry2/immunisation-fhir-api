"Utils for tests"

import operator
import unittest
from copy import deepcopy
from functools import reduce
from typing import Callable, Literal
from pydantic import ValidationError


def generate_field_location_for_questionnnaire_response(
    link_id: str, field_type: Literal["code", "display", "system"]
) -> str:
    """Generate the field location string for questionnaire response items"""
    return (
        "contained[0] -> resourceType[QuestionnaireResponse]: "
        + f"item[*] -> linkId[{link_id}]: answer[0] -> valueCoding -> {field_type}"
    )


def get_from_dict(data_dict, map_list):
    """takes a list of keys and returns the value in a nested dictionary"""
    return reduce(operator.getitem, map_list, data_dict)


def set_in_dict(data_dict, map_list, value):
    """takes a list of keys and sets the value in a nested dictionary"""
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


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
        """Test that a validator method accepts valid values"""
        for valid_item in valid_items_to_test:
            test_instance.assertEqual(validator(valid_item), valid_item)

    @staticmethod
    def string_invalid(
        test_instance: unittest.TestCase,
        validator: Callable,
        field_location: str,
        defined_length: int = None,
        max_length: int = 0,
        invalid_length_strings_to_test: list = None,
        predefined_values: tuple = None,
        invalid_strings_to_test: list = None,
    ):
        """
        Test that a validator method rejects the following invalid strings:
        * All invalid data types
        * If there is a defined_string_length: Strings of invalid length (defined by the argument
            invalid_length_strings_to_test), plus the empty string
        * If there is no defined_string_length: Empty strings
        * If there is a max length: Strings longer than max length (defined by the argument
            invalid_length_strings_to_test)
        * If there are predefined values: Invalid strings (i.e. not one of the predefined values) as
            defined by the argument invalid_strings_to_test

        NOTE: No validation of optional arguments will occur if the method is not given a list of
        values to test. This means that:
        * When optional arguments defined_length and max_length are given, the optional argument
            invalid_length_strings_to_test MUST also be given
        * When  optional argument predefined_lines is given, the optional argument
            invalid_strings_to_test MUST also be given.
        """
        # Test invalid data types
        for invalid_data_type_for_string in InvalidDataTypes.for_strings:
            with test_instance.assertRaises(TypeError) as error:
                validator(invalid_data_type_for_string)

            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a string",
            )

        # If there is a predefined string length, then test invalid string lengths, plus the
        # empty string, otherwise check the empty string only
        if defined_length:
            invalid_length_strings_to_test += [""]
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

        # If there is a max length, test strings which exceed that length
        if max_length:
            for invalid_length_string in invalid_length_strings_to_test:
                with test_instance.assertRaises(ValueError) as error:
                    validator(invalid_length_string)

                test_instance.assertEqual(
                    str(error.exception),
                    f"{field_location} must be {max_length} or fewer characters",
                )

        # If there are predefined values, then test strings which are
        # not in the set of predefined values
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
            invalid_length_lists_to_test), plus the empty list
        * If there is no predfined list length: Empty list
        * If there is a list of invalid_lists_with_non_string_data_types_to_test: Each of the
            items in the list, plus a list containing an empty string

        NOTE: No validation of optional arguments will occur if the method is not given a list of
        values to test. This means that:
        * When optional arguments predefined_list_length is given, the optional argument
            invalid_length_lists_to_test MUST also be given
        """
        # Test invalid data types
        for invalid_data_type_for_list in InvalidDataTypes.for_lists:
            with test_instance.assertRaises(TypeError) as error:
                validator(invalid_data_type_for_list)

            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be an array",
            )

        # If there is a predefined list length, then test invalid list lengths, plus the empty
        # list, otherwise check the empty list only
        if predefined_list_length:
            invalid_length_lists_to_test.append([])
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

    @staticmethod
    def boolean_invalid(
        test_instance: unittest.TestCase, validator: Callable, field_location: str
    ):
        """
        Test that a validator method rejects the following:
        * Non-boolean values
        """
        for invalid_data_type_for_boolean in InvalidDataTypes.for_booleans:
            with test_instance.assertRaises(TypeError) as error:
                validator(invalid_data_type_for_boolean)

            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a boolean",
            )


class GenericValidatorModelTests:
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
        keys_to_access_value: list,
        valid_items_to_test: list,
    ):
        """Test that a validator method accepts valid data when in a model"""
        valid_json_data = deepcopy(test_instance.json_data)
        for valid_item in valid_items_to_test:
            set_in_dict(valid_json_data, keys_to_access_value, valid_item)

            test_instance.assertTrue(test_instance.validator.validate(valid_json_data))

    @staticmethod
    def string_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
        keys_to_access_value: list,
        defined_length: int = None,
        max_length: int = None,
        invalid_length_strings_to_test: list = None,
        predefined_values: tuple = None,
        invalid_strings_to_test: list = None,
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
        * If is_mandatory_fhir is true: Value of None

        NOTE: No validation of optional arguments will occur if the method is not given a list of
        values to test. This means that:
        * When optional arguments defined_length and max_length are given, the optional argument
            invalid_length_strings_to_test MUST also be given
        * When optional argument predefined_lines is given, the optional argument
            invalid_strings_to_test MUST also be given.
        """
        invalid_json_data = deepcopy(test_instance.json_data)

        # If is mandatory FHIR, then for none type the model raises an
        # exception prior to running NHS pre-validators
        if is_mandatory_fhir:
            set_in_dict(invalid_json_data, keys_to_access_value, None)

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
            set_in_dict(
                invalid_json_data, keys_to_access_value, invalid_data_type_for_string
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
                set_in_dict(
                    invalid_json_data, keys_to_access_value, invalid_length_string
                )
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be 10 characters (type=value_error)"
                    in str(error.exception)
                )
        else:
            set_in_dict(invalid_json_data, keys_to_access_value, "")
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a non-empty string (type=value_error)"
                in str(error.exception)
            )

        # If there is a max_length, test strings which exceed that length
        if max_length:
            for invalid_length_string in invalid_length_strings_to_test:
                set_in_dict(
                    invalid_json_data, keys_to_access_value, invalid_length_string
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
                set_in_dict(invalid_json_data, keys_to_access_value, invalid_string)
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)
                test_instance.assertTrue(
                    f"{field_location} must be one of the following: "
                    + str(", ".join(predefined_values))
                    + " (type=value_error)"
                    in str(error.exception)
                )

    @staticmethod
    def list_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
        keys_to_access_value: list,
        predefined_list_length: int = None,
        invalid_length_lists_to_test: list = None,
        invalid_lists_with_non_string_data_types_to_test: list = None,
    ):
        """
        Test that a validator rejects the following invalid lists when in a model:
        * All invalid data types
        * If there is a predefined list length: Strings of invalid length (defined by the argument
            invalid_length_lists_to_test), plus the empty list
        * If there is no predfined list length: Empty list
        * If there is a list of invalid_lists_with_non_string_data_types_to_test: Each of the
            items in the list, plus a list containing an empty string

        NOTE: No validation of optional arguments will occur if the method is not given a list of
        values to test. This means that:
        * When optional arguments predefined_list_length is given, the optional argument
            invalid_length_lists_to_test MUST also be given
        """
        invalid_json_data = deepcopy(test_instance.json_data)

        # Test invalid data types
        for invalid_data_type_for_list in InvalidDataTypes.for_lists:
            set_in_dict(
                invalid_json_data, keys_to_access_value, invalid_data_type_for_list
            )

            # Check that we get the correct error message and that it contains type=value_error
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be an array (type=type_error)"
                in str(error.exception)
            )

        # If there is a predefined list length, then test invalid list lengths, plus the empty
        # list, otherwise check the empty list only
        if predefined_list_length:
            invalid_length_lists_to_test.append([])
            for invalid_length_list in invalid_length_lists_to_test:
                set_in_dict(
                    invalid_json_data, keys_to_access_value, invalid_length_list
                )
                with test_instance.assertRaises(ValueError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be an array of length 1 (type=value_error)"
                    in str(error.exception)
                )
        else:
            set_in_dict(invalid_json_data, keys_to_access_value, [])
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a non-empty array (type=value_error)"
                in str(error.exception)
            )

        # Tests invalid_lists_with_non_string_data_types_to_test (if provided)
        if invalid_lists_with_non_string_data_types_to_test:
            # Test each invalid list
            for invalid_list in invalid_lists_with_non_string_data_types_to_test:
                set_in_dict(invalid_json_data, keys_to_access_value, invalid_list)
                with test_instance.assertRaises(ValidationError) as error:
                    test_instance.validator.validate(invalid_json_data)

                test_instance.assertTrue(
                    f"{field_location} must be an array of strings (type=type_error)"
                    in str(error.exception)
                )

            # Test empty string in list
            set_in_dict(invalid_json_data, keys_to_access_value, [""])
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
        keys_to_access_value: list,
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
            set_in_dict(
                invalid_json_data, keys_to_access_value, invalid_data_type_for_string
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a string (type=type_error)"
                in str(error.exception)
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
            set_in_dict(invalid_json_data, keys_to_access_value, invalid_date_format)
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f'{field_location} must be a string in the format "YYYY-MM-DD" (type=value_error)'
                in str(error.exception)
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
            set_in_dict(invalid_json_data, keys_to_access_value, invalid_date)
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a valid date (type=value_error)"
                in str(error.exception)
            )

    @staticmethod
    def boolean_invalid(
        test_instance: unittest.TestCase,
        field_location: str,
        keys_to_access_value: list,
    ):
        """Test that a validator rejects any non-boolean value when in a model"""

        invalid_json_data = deepcopy(test_instance.json_data)

        # Test invalid data types
        for invalid_data_type_for_boolean in InvalidDataTypes.for_booleans:
            set_in_dict(
                invalid_json_data, keys_to_access_value, invalid_data_type_for_boolean
            )
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                f"{field_location} must be a boolean (type=type_error)"
                in str(error.exception)
            )
