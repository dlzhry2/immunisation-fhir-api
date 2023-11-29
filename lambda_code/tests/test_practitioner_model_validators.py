"""Tests for the NHS Practitioner model validators"""

import unittest
import sys
import os
import json
from copy import deepcopy

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_practitioner import PractitionerValidator


class TestNHSPractitionerModelValidationRules(unittest.TestCase):
    """Test NHS specific practitioner validation rules on the model"""

    @classmethod
    def setUpClass(cls):
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"
        cls.practitioner_file_path = f"{cls.data_path}/sample_practitioner_event.json"
        with open(cls.practitioner_file_path, "r", encoding="utf-8") as f:
            cls.practitioner_json_data = json.load(f)
        with open(cls.practitioner_file_path, "r", encoding="utf-8") as f:
            cls.untouched_practitioner_json_data = json.load(f)
        cls.practitioner_validator = PractitionerValidator()
        cls.practitioner_validator.add_custom_root_validators()
        cls.invalid_data_types_for_mandatory_strings = [
            None,
            "",
            {},
            [],
            (),
            {"InvalidKey": "InvalidValue"},
            ["Invalid"],
            ("Invalid1", "Invalid2"),
        ]
        cls.invalid_data_types_for_optional_strings = [
            {"InvalidKey": "InvalidValue"},
            ["Invalid"],
            ("Invalid1", "Invalid2"),
        ]

    def setUp(self):
        """Ensure that good data is not inadvertently amended by the tests"""
        self.assertEqual(
            self.untouched_practitioner_json_data, self.practitioner_json_data
        )

    def test_model_practitioner_validator(self):
        """Test validator model accepts valid data"""
        self.assertTrue(
            self.practitioner_validator.validate(self.practitioner_json_data)
        )

    def test_model_invalid_name_given(self):
        """Test validator model rejects invalid name_given"""
        invalid_names_given = self.invalid_data_types_for_optional_strings
        invalid_json_data = deepcopy(self.practitioner_json_data)
        for invalid_name_given in invalid_names_given:
            invalid_json_data["name"][0]["given"][0] = invalid_name_given
            with self.assertRaises(ValueError):
                self.practitioner_validator.validate(invalid_json_data)
