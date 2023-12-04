"""Test patient pre-validation methods"""

import unittest

from models.patient_pre_validators import PatientPreValidators


class TestPrePatientMethodValidators(unittest.TestCase):
    """Test patient pre-validation methods"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
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
            {"InvalidKey": "InvalidValue"},
            ["Invalid"],
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

        # set up invalid data types for dicts
        cls.invalid_data_types_for_dicts = [
            None,
            -1,
            0,
            0.0,
            1,
            True,
            [],
            "",
            ["Invalid"],
            "Invalid",
        ]

    def test_pre_name_valid(self):
        """Test PatientPreValidators.name"""
        # Test valid data
        valid_name = [{"family": "Test"}]
        self.assertEqual(
            PatientPreValidators.name(valid_name),
            valid_name,
        )

    def test_pre_name_invalid(self):
        """Test PatientPreValidators.name"""

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            with self.assertRaises(TypeError) as error:
                PatientPreValidators.name(invalid_data_type_for_list)

            self.assertEqual(
                str(error.exception),
                "name must be an array",
            )

        # Test invalid list length
        invalid_names = [[], [{"family": "Test"}, {"family": "Test"}]]
        for invalid_name in invalid_names:
            with self.assertRaises(ValueError) as error:
                PatientPreValidators.name(invalid_name)

            self.assertEqual(
                str(error.exception),
                "name must be an array of length 1",
            )

    def test_pre_name_given_valid(self):
        """Test PatientPreValidators.name_given"""

        # Test valid data
        valid_names_given = [["Test"], ["Test1", "Test2"]]
        for valid_name_given in valid_names_given:
            self.assertEqual(
                PatientPreValidators.name_given(valid_name_given),
                valid_name_given,
            )

    def test_pre_name_given_invalid(self):
        """Test PatientPreValidators.name_given"""

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            with self.assertRaises(TypeError) as error:
                PatientPreValidators.name_given(invalid_data_type_for_list)

            self.assertEqual(
                str(error.exception),
                "name -> given must be an array",
            )

        # Test empty list is invalid
        with self.assertRaises(ValueError) as error:
            PatientPreValidators.name_given([])
        self.assertEqual(
            str(error.exception),
            "name -> given must be a non-empty array",
        )

        # Test invalid data types for list items
        invalid_names_given = [[1, "test"], ["test", False], [["Test1"]]]
        for invalid_name_given in invalid_names_given:
            with self.assertRaises(TypeError) as error:
                PatientPreValidators.name_given(invalid_name_given)

            self.assertEqual(
                str(error.exception),
                "name -> given must be an array of strings",
            )

        # Test invalid string (empty) in list
        with self.assertRaises(ValueError) as error:
            PatientPreValidators.name_given([""])
        self.assertEqual(
            str(error.exception),
            "name -> given must be an array of non-empty strings",
        )

    def test_pre_name_family_valid(self):
        """Test PatientPreValidators.name_family"""

        # Test valid data
        valid_name_family = "test"
        self.assertEqual(
            PatientPreValidators.name_family(valid_name_family),
            valid_name_family,
        )

    def test_pre_name_family_invalid(self):
        """Test PatientPreValidators.name_family"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                PatientPreValidators.name_family(invalid_data_type_for_string)

            self.assertEqual(
                str(error.exception),
                "name -> family must be a string",
            )

        # Test empty string is invalid
        with self.assertRaises(ValueError) as error:
            PatientPreValidators.name_family("")
        self.assertEqual(
            str(error.exception),
            "name -> family must be a non-empty string",
        )

    def test_pre_birth_date_valid(self):
        """Test PatientPreValidators.birth_date"""

        # Test valid data
        valid_birth_dates = ["2000-01-01", "1933-12-31"]
        for valid_birth_date in valid_birth_dates:
            self.assertEqual(
                PatientPreValidators.birth_date(valid_birth_date),
                valid_birth_date,
            )

    def test_pre_birth_date_invalid(self):
        """Test PatientPreValidators.birth_date"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                PatientPreValidators.birth_date(invalid_data_type_for_string)

            self.assertEqual(
                str(error.exception),
                "birthDate must be a string",
            )

        # Test invalid date string formats
        invalid_birth_dates = [
            "",
            "invalid",
            "20000101",
            "2000-01-011",
            "12000-01-01",
            "12000-01-021",
            "99-01-01",
            "01-01-99",
            "01-01-1999",
        ]
        for invalid_birth_date in invalid_birth_dates:
            with self.assertRaises(ValueError) as error:
                PatientPreValidators.birth_date(invalid_birth_date)
            self.assertEqual(
                str(error.exception),
                'birthDate must be a string in the format "YYYY-MM-DD"',
            )

        # Test invalid dates
        invalid_birth_dates = [
            "2000-00-01",
            "2000-13-01",
            "2000-01-00",
            "2000-01-32",
            "2000-02-30",
        ]
        for invalid_birth_date in invalid_birth_dates:
            with self.assertRaises(ValueError) as error:
                PatientPreValidators.birth_date(invalid_birth_date)
            self.assertEqual(
                str(error.exception),
                "birthDate must be a valid date",
            )
