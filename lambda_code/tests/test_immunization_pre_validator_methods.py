"""Test immunization pre-validation methods"""

import unittest

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

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.pre_patient_identifier_value(
                    invalid_data_type_for_string
                )

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> value must be a string",
            )

        # Test invalid string lengths
        invalid_patient_identifier_values = ["123456789", "12345678901", ""]
        for invalid_patient_identifier_value in invalid_patient_identifier_values:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.pre_patient_identifier_value(
                    invalid_patient_identifier_value
                )

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> value must be 10 characters",
            )

    def test_pre_occurrence_date_time_valid(self):
        """Test ImmunizationPreValidators.occurrence_date_time"""

        # Test valid data
        valid_occurrence_date_times = [
            "2000-01-01T00:00:00",
            "2000-01-01T22:22:22",
            "1933-12-31T11:11:11+12:45",
        ]
        for valid_occurrence_date_time in valid_occurrence_date_times:
            self.assertEqual(
                ImmunizationPreValidators.occurrence_date_time(
                    valid_occurrence_date_time
                ),
                valid_occurrence_date_time,
            )

    def test_pre_occurrence_date_time_invalid(self):
        """Test ImmunizationPreValidators.occurrence_date_time"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.occurrence_date_time(
                    invalid_data_type_for_string
                )

            self.assertEqual(
                str(error.exception),
                "occurrenceDateTime must be a string",
            )

        # Test invalid date string formats
        invalid_occurrence_date_times = [
            "",
            "invalid",
            "20000101",
            "20000101000000",
            "200001010000000000",
            "2000-01-01",
            "2000-01-01T00:00:001",
            "12000-01-01T00:00:00+00:00",
            "12000-01-02T00:00:001",
            "12000-01-02T00:00:00+00:001",
            "2000-01-0122:22:22",
            "2000-01-0122:22:22+00:00",
            "2000-01-01T22:22:2200:00",
            "2000-01-01T22:22:22+0000",
            "99-01-01T00:00:00",
            "01-01-99T00:00:00",
            "01-01-1999T00:00:00",
        ]
        for invalid_occurrence_date_time in invalid_occurrence_date_times:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.occurrence_date_time(
                    invalid_occurrence_date_time
                )
            self.assertEqual(
                str(error.exception),
                'occurrenceDateTime must be a string in the format "YYYY-MM-DDThh:mm:ss" '
                + 'or "YYYY-MM-DDThh:mm:ss+zz"',
            )

        # Test invalid dates
        invalid_occurrence_date_times = [
            "2000-00-01T00:00:00",
            "2000-13-01T00:00:00",
            "2000-01-00T00:00:00",
            "2000-01-32T00:00:00",
            "2000-02-30T00:00:00",
            "2000-01-01T24:00:00",
            "2000-01-01T00:60:00",
            "2000-01-01T00:00:60",
            "2000-01-01T00:00:00+24:00",
            "2000-01-01T00:00:00+00:60",
        ]
        for invalid_occurrence_date_time in invalid_occurrence_date_times:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.occurrence_date_time(
                    invalid_occurrence_date_time
                )
            self.assertEqual(
                str(error.exception),
                "occurrenceDateTime must be a valid datetime",
            )
