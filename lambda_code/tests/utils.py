"Utils for tests"

invalid_data_types_for_strings = [
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

invalid_data_types_for_lists = [
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

invalid_data_types_for_booleans = [
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

invalid_data_types_for_integers = [
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


def generic_string_validator_valid_tests(
    test_class,
    validator,
    valid_strings_to_test: list,
):
    """Test that a validator method accepts valid strings"""
    for valid_string in valid_strings_to_test:
        test_class.assertEqual(validator(valid_string), valid_string)


def generic_string_validator_invalid_tests(
    test_class,
    validator,
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
    for invalid_data_type_for_string in invalid_data_types_for_strings:
        with test_class.assertRaises(TypeError) as error:
            validator(invalid_data_type_for_string)

        test_class.assertEqual(
            str(error.exception),
            f"{field_location} must be a string",
        )

    # If there is a predefined string length, then test invalid string lengths,
    # otherwise check the empty string only
    if predefined_string_length:
        for invalid_length_string in invalid_length_strings_to_test:
            with test_class.assertRaises(ValueError) as error:
                validator(invalid_length_string)

            test_class.assertEqual(
                str(error.exception),
                f"{field_location} must be {predefined_string_length} characters",
            )
    else:
        with test_class.assertRaises(ValueError) as error:
            validator("")
        test_class.assertEqual(
            str(error.exception),
            f"{field_location} must be a non-empty string",
        )
