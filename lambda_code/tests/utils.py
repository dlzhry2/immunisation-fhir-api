"Utils for tests"

from typing import Callable, Literal


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
    def string_valid(
        test_instance,
        validator: Callable,
        valid_strings_to_test: list,
    ):
        """Test that a validator method accepts valid strings"""
        for valid_string in valid_strings_to_test:
            test_instance.assertEqual(validator(valid_string), valid_string)

    @staticmethod
    def string_invalid(
        test_instance,
        validator: Callable,
        field_location: str,
        predefined_string_length: int = None,
        invalid_length_strings_to_test: list = None,
    ):
        """
        Test that a validator method rejects the following invalid strings:
        * All invalid data types are rejected
        * If there is a predefined string length: Strings of invalid length (defined by the argument
            invalid_length_strings_to_test - this should include an empty string)
        * If there is no predfined string length: Empty strings
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
        if predefined_string_length:
            for invalid_length_string in invalid_length_strings_to_test:
                with test_instance.assertRaises(ValueError) as error:
                    validator(invalid_length_string)

                test_instance.assertEqual(
                    str(error.exception),
                    f"{field_location} must be {predefined_string_length} characters",
                )
        else:
            with test_instance.assertRaises(ValueError) as error:
                validator("")
            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a non-empty string",
            )

    @staticmethod
    def list_valid(
        test_instance,
        validator: Callable,
        valid_lists_to_test: list,
    ):
        """Test that a validator method accepts valid lists"""
        for valid_list in valid_lists_to_test:
            test_instance.assertEqual(validator(valid_list), valid_list)

    @staticmethod
    def list_invalid(
        test_instance,
        validator: Callable,
        field_location: str,
        predefined_list_length: int = None,
        invalid_length_lists_to_test: list = None,
    ):
        """
        Test that a validator method rejects the following invalid lists:
        * All invalid data types are rejected
        * If there is a predefined list length: Strings of invalid length (defined by the argument
            invalid_length_lists_to_test - this should include an empty list)
        * If there is no predfined list length: Empty lists
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
                validator("")
            test_instance.assertEqual(
                str(error.exception),
                f"{field_location} must be a non-empty list",
            )
