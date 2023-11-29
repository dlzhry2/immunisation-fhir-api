"""Tests for the NHS Patient method validators"""

import unittest
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.nhs_validators import NHSPatientValidators


class TestNHSPatientMethodValidationRules(unittest.TestCase):
    """Test NHS specific patient validation rules"""

    @classmethod
    def setUpClass(cls):
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
