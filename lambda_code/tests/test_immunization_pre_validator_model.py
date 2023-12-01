"""Test immunization pre validation rules on the model"""
import unittest
import sys
import os
import json
from copy import deepcopy
from pydantic import ValidationError

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_immunization import ImmunizationValidator


class TestImmunizationModelPreValidationRules(unittest.TestCase):
    """
    Test immunization pre validation rules on the model

    Notes:-
    TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
    this happens, the error message is suffixed with the type of error e.g. type_error or
    value_error. This is why the tests check for the type of error in the error message.

    """

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample immunization event JSON data
        cls.immunization_file_path = f"{cls.data_path}/sample_immunization_event.json"
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.immunization_json_data = json.load(f)

        # set up the untouched sample immunization event JSON data
        cls.untouched_immunization_json_data = deepcopy(cls.immunization_json_data)

        # set up the validator and add custom root validators
        cls.immunization_validator = ImmunizationValidator()
        cls.immunization_validator.add_custom_root_validators()

        # set up invalid data types for strings
        cls.invalid_data_types_for_strings = [
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

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(
            self.untouched_immunization_json_data, self.immunization_json_data
        )

    def test_model_pre_validate_valid_patient_identifier_value(self):
        """Test pre_validate_patient_identifier_value accepts valid values when in a model"""
        valid_patient_identifier_value = "1234567890"
        valid_json_data = deepcopy(self.immunization_json_data)
        valid_json_data["patient"]["identifier"][
            "value"
        ] = valid_patient_identifier_value

        self.assertTrue(self.immunization_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_patient_identifier_value(self):
        """Test pre_validate_patient_identifier_value rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.immunization_json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["patient"]["identifier"][
                "value"
            ] = invalid_data_type_for_string

            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.immunization_validator.validate(invalid_json_data)

            self.assertTrue(
                "patient -> identifier -> value must be a string (type=type_error)"
                in str(error.exception)
            )

        # Test invalid string lengths
        invalid_patient_identifier_values = ["123456789", "12345678901", ""]
        for invalid_patient_identifier_value in invalid_patient_identifier_values:
            invalid_json_data["patient"]["identifier"][
                "value"
            ] = invalid_patient_identifier_value

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.immunization_validator.validate(invalid_json_data)

            self.assertTrue(
                "patient -> identifier -> Value must be 10 characters (type=value_error)"
                in str(error.exception)
            )
