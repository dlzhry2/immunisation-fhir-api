"""Tests for the NHS Practitioner method validators"""

import unittest
import sys
import os
from icecream import ic

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.old_nhs_validators import NHSPractitionerValidators


class TestNHSPractitionerValidationRules(unittest.TestCase):
    """Test NHS specific practitioner validation rules"""

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
        cls.invalid_data_types_for_optional_strings = [
            {"InvalidKey": "InvalidValue"},
            ["Invalid"],
            ("Invalid1", "Invalid2"),
        ]

    def test_valid_performing_professional_forename(self):
        """Test that the performing professional forename accepts valid combinations"""
        valid_combinations = [
            {
                "disease_type": "FLU",
                "forename": "Test",
                "surname": "Test",
            },
            {
                "disease_type": "FLU",
                "forename": None,
                "surname": None,
            },
            {
                "disease_type": "MMR",
                "forename": None,
                "surname": None,
            },
        ]
        for valid_combination in valid_combinations:
            self.assertEqual(
                NHSPractitionerValidators.validate_performing_professional_forename(
                    valid_combination["disease_type"],
                    valid_combination["forename"],
                    valid_combination["surname"],
                ),
                valid_combination["forename"],
            )

    def test_invalid_performing_professional_forename(self):
        """Test that the performing professional forename rejects invalid combinations"""
        invalid_combinations = [
            {
                "disease_type": "FLU",
                "forename": None,
                "surname": "Test",
                "expected_error": " ".join(
                    (
                        "If PERFORMING_PROFESSIONAL_SURNAME is given,",
                        "PERFORMING_PROFESSIONAL_FORENAME must also be given",
                    )
                ),
            },
            {
                "disease_type": "MMR",
                "forename": "Test",
                "surname": None,
                "expected_error": " ".join(
                    (
                        "PERFORMING_PROFESSIONAL_FORENAME",
                        "is not allowed for: ('HPV', 'MMR')",
                    ),
                ),
            },
        ]

        for invalid_combination in invalid_combinations:
            with self.assertRaises(ValueError) as e:
                NHSPractitionerValidators.validate_performing_professional_forename(
                    invalid_combination["disease_type"],
                    invalid_combination["forename"],
                    invalid_combination["surname"],
                )
            self.assertEqual(invalid_combination["expected_error"], str(e.exception))

    def test_valid_performing_professional_surname(self):
        """Test that the performing professional surname accepts valid combinations"""
        valid_combinations = [
            {
                "disease_type": "FLU",
                "surname": "Test",
                "forename": "Test",
            },
            {
                "disease_type": "FLU",
                "surname": None,
                "forename": None,
            },
            {
                "disease_type": "MMR",
                "surname": None,
                "forename": None,
            },
        ]
        for valid_combination in valid_combinations:
            self.assertEqual(
                NHSPractitionerValidators.validate_performing_professional_surname(
                    valid_combination["disease_type"],
                    valid_combination["surname"],
                    valid_combination["forename"],
                ),
                valid_combination["surname"],
            )

    def test_invalid_performing_professional_surname(self):
        """Test that the performing professional surname rejects invalid combinations"""
        invalid_combinations = [
            {
                "disease_type": "FLU",
                "surname": None,
                "forename": "Test",
                "expected_error": " ".join(
                    (
                        "If PERFORMING_PROFESSIONAL_FORENAME is given,",
                        "PERFORMING_PROFESSIONAL_SURNAME must also be given",
                    )
                ),
            },
            {
                "disease_type": "MMR",
                "surname": "Test",
                "forename": None,
                "expected_error": " ".join(
                    (
                        "PERFORMING_PROFESSIONAL_SURNAME",
                        "is not allowed for: ('HPV', 'MMR')",
                    ),
                ),
            },
        ]

        for invalid_combination in invalid_combinations:
            with self.assertRaises(ValueError) as e:
                NHSPractitionerValidators.validate_performing_professional_surname(
                    invalid_combination["disease_type"],
                    invalid_combination["surname"],
                    invalid_combination["forename"],
                )
            self.assertEqual(invalid_combination["expected_error"], str(e.exception))
