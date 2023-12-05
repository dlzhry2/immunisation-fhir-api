"""Test immunization pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from pydantic import ValidationError


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
                "patient -> identifier -> value must be 10 characters (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_occurrence_date_time(self):
        """Test pre_validate_occurrence_date_time accepts valid values when in a model"""
        valid_occurrence_date_times = [
            "2000-01-01T00:00:00",
            "2000-01-01T22:22:22",
            "1933-12-31T11:11:11+12:45",
        ]
        valid_json_data = deepcopy(self.immunization_json_data)
        for valid_occurrence_date_time in valid_occurrence_date_times:
            valid_json_data["occurrenceDateTime"] = valid_occurrence_date_time
            self.assertTrue(self.immunization_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_occurrence_date_time(self):
        """Test pre_validate_occurrence_date_time rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.immunization_json_data)

        # Test none (this should be rejected by the model prior to the pre-validate function
        # running as FHIR cardinality is 1..1)
        invalid_json_data["occurrenceDateTime"] = None
        # Check that we get the correct error message and that it contains type=type_error
        with self.assertRaises(ValidationError) as error:
            self.immunization_validator.validate(invalid_json_data)

        self.assertTrue(
            "Expect any of field value from this list "
            + "['occurrenceDateTime', 'occurrenceString']. (type=value_error)"
            in str(error.exception)
        )

        # Test invalid data types (other than none)
        for invalid_data_type_for_string in filter(
            None, self.invalid_data_types_for_strings
        ):
            invalid_json_data["occurrenceDateTime"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.immunization_validator.validate(invalid_json_data)

            self.assertTrue(
                "occurrenceDateTime must be a string (type=type_error)"
                in str(error.exception)
            )

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
            invalid_json_data["occurrenceDateTime"] = invalid_occurrence_date_time

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.immunization_validator.validate(invalid_json_data)

            self.assertTrue(
                'occurrenceDateTime must be a string in the format "YYYY-MM-DDThh:mm:ss" '
                + 'or "YYYY-MM-DDThh:mm:ss+zz" (type=value_error)'
                in str(error.exception)
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
            invalid_json_data["occurrenceDateTime"] = invalid_occurrence_date_time

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.immunization_validator.validate(invalid_json_data)

            self.assertTrue(
                "occurrenceDateTime must be a valid datetime (type=value_error)"
                in str(error.exception)
            )
