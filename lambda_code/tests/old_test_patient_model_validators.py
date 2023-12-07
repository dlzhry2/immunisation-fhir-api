"""Tests for the NHS Patient model validators"""

import unittest
import sys
import os
import json
from copy import deepcopy

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_patient import PatientValidator


class TestNHSPatientModelValidationRules(unittest.TestCase):
    """Test NHS specific patient validation rules on the model"""

    @classmethod
    def setUpClass(cls):
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"
        cls.patient_file_path = f"{cls.data_path}/sample_patient_event.json"
        with open(cls.patient_file_path, "r", encoding="utf-8") as f:
            cls.patient_json_data = json.load(f)
        with open(cls.patient_file_path, "r", encoding="utf-8") as f:
            cls.untouched_json_data = json.load(f)
        cls.patient_validator = PatientValidator()
        cls.patient_validator.add_custom_root_validators()
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

    def setUp(self):
        """Ensure that good data is not inadvertently amended by the tests"""
        self.assertEqual(self.untouched_json_data, self.patient_json_data)

    def test_model_patient_validator(self):
        """Test validator model accepts valid data"""
        self.assertTrue(self.patient_validator.validate(self.patient_json_data))

    def test_model_invalid_name_given(self):
        """Test validator model rejects invalid name_given"""
        invalid_names_given = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_name_given in invalid_names_given:
            invalid_json_data["name"][0]["given"][0] = invalid_name_given
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)

    def test_model_invalid_name_family(self):
        """Test validator model rejects invalid name_family"""
        invalid_names_family = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_name_family in invalid_names_family:
            invalid_json_data["name"][0]["family"] = invalid_name_family
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)

    def test_model_invalid_birth_date(self):
        """Test validator model rejects invalid birth_date"""
        invalid_birth_dates = ["2000-13-01", "20010101", 20010101]
        invalid_birth_dates += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_birth_date in invalid_birth_dates:
            invalid_json_data["birthDate"] = invalid_birth_date
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)

    def test_model_invalid_gender(self):
        """Test validator model rejects invalid gender"""
        invalid_genders = [
            "0",
            "1",
            "2",
            "9",
            "10",
            0,
            1,
            2,
            9,
            10,
            "Male",
            "Female",
            "Unknown",
            "Other",
        ]
        invalid_genders += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_gender in invalid_genders:
            invalid_json_data["gender"] = invalid_gender
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)

    def test_model_invalid_address_postal_code(self):
        """Test validator model rejects invalid address_postal_code"""
        address_postal_codes = [
            "AA000 00AA",
            "SW1  1AA",
            "SW 1 1A",
            "AAA0000AA",
            "SW11AA",
        ]
        address_postal_codes += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for address_postal_code in address_postal_codes:
            invalid_json_data["address"][0]["postalCode"] = address_postal_code
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)
