"""Test patient pre validation rules on the model"""
import unittest
import sys
import os
import json
from copy import deepcopy

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_patient import PatientValidator


class TestPatientModelPreValidationRules(unittest.TestCase):
    """Test patient pre validation rules on the model"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample patient event JSON data
        cls.patient_file_path = f"{cls.data_path}/sample_patient_event.json"
        with open(cls.patient_file_path, "r", encoding="utf-8") as f:
            cls.patient_json_data = json.load(f)

        # set up the untouched sample patient event JSON data
        cls.untouched_patient_json_data = deepcopy(cls.patient_json_data)

        # set up the validator and add custom root validators
        cls.patient_validator = PatientValidator()
        cls.patient_validator.add_custom_root_validators()

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

        # set up invalid data types for lists
        cls.invalid_data_types_for_lists = [
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

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_patient_json_data, self.patient_json_data)

    def test_model_pre_validate_valid_name(self):
        """Test pre_validate_name accepts valid values when in a model"""
        valid_name = [{"family": "Test"}]
        valid_json_data = deepcopy(self.patient_json_data)
        valid_json_data["name"] = valid_name

        self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_valid_name_given(self):
        """Test pre_validate_name_given accepts valid values when in a model"""
        valid_names_given = [["Test"], ["Test1", "Test2"]]
        valid_json_data = deepcopy(self.patient_json_data)
        valid_json_data["name"]["given"] = valid_names_given

        self.assertTrue(self.patient_validator.pre_validate_name_given(valid_json_data))

    def test_model_pre_validate_invalid_name_given(self):
        """Test pre_validate_name_given rejects invalid values when in a model"""
        invalid_name_givens = ["123456789", "12345678901", ""]
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_name_given in invalid_name_givens:
            invalid_json_data["patient"]["identifier"]["value"] = invalid_name_given
            with self.assertRaises(ValueError) as error:
                self.patient_validator.pre_validate_name_given(invalid_json_data)

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> Value must be 10 characters",
            )

        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["patient"]["identifier"][
                "value"
            ] = invalid_data_type_for_string
            with self.assertRaises(TypeError) as error:
                self.patient_validator.pre_validate_name_given(invalid_json_data)

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> value must be a string",
            )
