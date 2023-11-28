"""Tests for the NHS Patient validators"""

import unittest
import sys
import os
import json
from copy import deepcopy

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.nhs_validators import NHSPatientValidators
from models.fhir_patient import PatientValidator


class TestNHSPatientValidationRules(unittest.TestCase):
    """Test NHS specific patient validation rules"""

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

    def test_patient_validator(self):
        """Test validator model accepts valid data"""
        self.assertTrue(self.patient_validator.validate(self.patient_json_data))

    def test_valid_name_given(self):
        """Test name_given (forename) accepts valid name"""
        valid_name_given = "Valid_name_given"
        self.assertTrue(NHSPatientValidators.validate_name_given(valid_name_given))

    def test_invalid_name_given(self):
        """Test name_given (forename) validator rejects invalid name"""
        invalid_names_given = [None, ""]
        for invalid_name_given in invalid_names_given:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_name_given(invalid_name_given)

    def test_model_name_given(self):
        """Test validator model rejects invalid name_given"""
        invalid_names_given = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_name_given in invalid_names_given:
            invalid_json_data["name"][0]["given"][0] = invalid_name_given
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)

    def test_valid_name_family(self):
        """Test name_family (surname) validator accepts valid name"""
        valid_name_family = "Valid_name_family"
        self.assertTrue(NHSPatientValidators.validate_name_family(valid_name_family))

    def test_invalid_name_family(self):
        """Test name_family (surname) validator rejects invalid name"""
        invalid_names_family = [None, ""]
        for invalid_name_family in invalid_names_family:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_name_family(invalid_name_family)

    def test_model_name_family(self):
        """Test validator model rejects invalid name_family"""
        invalid_names_family = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_name_family in invalid_names_family:
            invalid_json_data["name"][0]["family"] = invalid_name_family
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)

    def test_valid_birth_date(self):
        """Test birth_date accepts valid birth date"""
        valid_birth_date = "2000-01-01"
        self.assertTrue(NHSPatientValidators.validate_birth_date(valid_birth_date))

    def test_invalid_birth_date(self):
        """Test birth_date rejects invalid birth_date"""
        invalid_birth_dates = ["2000-13-01", "20001201", None, ""]
        for invalid_birth_date in invalid_birth_dates:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_birth_date(invalid_birth_date)

    def test_model_birth_date(self):
        """Test validator model rejects invalid birth_date"""
        invalid_birth_dates = ["2000-13-01", "20010101", 20010101]
        invalid_birth_dates += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.patient_json_data)
        for invalid_birth_date in invalid_birth_dates:
            invalid_json_data["birthDate"] = invalid_birth_date
            with self.assertRaises(ValueError):
                self.patient_validator.validate(invalid_json_data)

    def test_valid_gender(self):
        """Test gender validator accepts valid gender"""
        valid_genders = ["male", "female", "other", "unknown"]
        for valid_gender in valid_genders:
            self.assertTrue(NHSPatientValidators.validate_gender(valid_gender))

    def test_invalid_gender(self):
        """Test gender validator rejects invalid gender"""
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
            None,
            "",
        ]
        for invalid_gender in invalid_genders:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_gender(invalid_gender)

    def test_model_gender(self):
        """Test validator model rejects invalid gender"""
        invalid_genders = [-1, 10, "-1", "10", "Male", "Unknown"]
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

    def test_valid_address_postal_code(self):
        """Test address_postal_code validator accepts valid address_postal_code"""
        valid_address_postal_codes = ["AA00 00AA", "A0 0AA"]
        for valid_address_postal_code in valid_address_postal_codes:
            self.assertTrue(
                NHSPatientValidators.validate_address_postal_code(
                    valid_address_postal_code
                )
            )

    def test_invalid_address_postal_code(self):
        """Test person_postcode validator rejects invalid person postcode"""
        invalid_address_postal_codes = [
            "AA000 00AA",
            "SW1  1AA",
            "SW 1 1A",
            "AAA0000AA",
            "SW11AA",
            None,
            "",
        ]
        for invalid_address_postal_code in invalid_address_postal_codes:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_address_postal_code(
                    invalid_address_postal_code
                )

    def test_model_address_postal_code(self):
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
