"""Test immunization pre-validation methods"""

import unittest
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.immunization_pre_validators import ImmunizationPreValidators


class TestPreImmunizationMethodValidators(unittest.TestCase):
    """Test immunization pre-validation methods"""

    @classmethod
    def setUpClass(cls):
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

    def test_pre_patient_identifier_value_valid(self):
        """Test pre_patient_identifier_value"""
        valid_patient_identifier_value = "1234567890"
        self.assertEqual(
            ImmunizationPreValidators.pre_patient_identifier_value(
                valid_patient_identifier_value
            ),
            "1234567890",
        )

    def test_pre_patient_identifier_value_invalid(self):
        """Test pre_patient_identifier_value"""
        invalid_patient_identifier_values = ["123456789", "12345678901", ""]
        for invalid_patient_identifier_value in invalid_patient_identifier_values:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.pre_patient_identifier_value(
                    invalid_patient_identifier_value
                )

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> Value must be 10 characters",
            )

        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.pre_patient_identifier_value(
                    invalid_data_type_for_string
                )

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> value must be a string",
            )
