"""Tests for the NHS Immunization validators"""

import unittest
import sys
import os
import json
from datetime import datetime
from copy import deepcopy

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_immunization import ImmunizationValidator
from models.nhs_validators import NHSImmunizationValidators


class TestNHSImmunizationValidationRules(unittest.TestCase):
    """Test NHS specific immunization validation rules"""

    @classmethod
    def setUpClass(cls):
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"
        cls.immunization_file_path = f"{cls.data_path}/sample_immunization_event.json"
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.immunization_json_data = json.load(f)
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.untouched_immunization_json_data = json.load(f)
        cls.immunization_validator = ImmunizationValidator()
        cls.immunization_validator.add_custom_root_validators()

    def setUp(self):
        """Ensure that good data is not inadvertently amended by the tests"""
        self.assertEqual(
            self.untouched_immunization_json_data, self.immunization_json_data
        )

    def test_immunization_validator(self):
        """Test validator model accepts valid data"""
        self.assertTrue(
            self.immunization_validator.validate(self.immunization_json_data)
        )

    def test_valid_patient_identifier_value(self):
        """Test patient_identifier_value (NHS number) validator accepts valid number"""
        valid_patient_identifier_values = ["1234567890", " 12345 67890 "]
        for valid_patient_identifier_value in valid_patient_identifier_values:
            self.assertTrue(
                NHSImmunizationValidators.validate_patient_identifier_value(
                    valid_patient_identifier_value
                )
            )

    def test_invalid_patient_identifier_value(self):
        """Test patient_identifier_value (NHS number) validator rejects invalid number"""
        invalid_patient_identifier_value = "123456789"
        with self.assertRaises(ValueError):
            NHSImmunizationValidators.validate_patient_identifier_value(
                invalid_patient_identifier_value
            )

    def test_model_invalid_patient_identifier_value(self):
        """Test validator model rejects invalid patient_identifier_value"""
        invalid_json_data = deepcopy(self.immunization_json_data)
        invalid_json_data["patient"]["identifier"]["value"] = "123456789"
        with self.assertRaises(ValueError):
            self.immunization_validator.validate(invalid_json_data)

    def test_valid_occurrence_date_time(self):
        """ "Test occurrence_date_time validator returns valid occurrence date and time in correct datetime format"""
        valid_occurrence_date_times = [
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
            datetime.strptime("2021-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
            datetime.strptime("2021-01-01T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
        ]
        expected_occurrence_date_time = "2021-01-01T00:00:00+00:00"

        for valid_occurrence_date_time in valid_occurrence_date_times:
            returned_occurrence_date_time = (
                NHSImmunizationValidators.validate_occurrence_date_time(
                    valid_occurrence_date_time
                )
            )
            self.assertEqual(
                returned_occurrence_date_time, expected_occurrence_date_time
            )

        # Test unusual timezone
        valid_occurrence_date_time = datetime.strptime(
            "2022-04-05T13:42:11+12:45", "%Y-%m-%dT%H:%M:%S%z"
        )
        expected_occurrence_date_time = "2022-04-05T13:42:11+12:45"
        returned_occurrence_date_time = (
            NHSImmunizationValidators.validate_occurrence_date_time(
                valid_occurrence_date_time
            )
        )
        self.assertEqual(returned_occurrence_date_time, expected_occurrence_date_time)

    def test_invalid_occurrence_date_time(self):
        """Test occurrence_date_and_time validator rejects invalid occurrence date and time"""
        invalid_occurrence_date_times = [None, ""]
        for invalid_occurrence_date_time in invalid_occurrence_date_times:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_occurrence_date_time(
                    invalid_occurrence_date_time
                )

    def test_model_occurrence_date_time(self):
        """Test validator model rejects invalid occurrence_date_time"""
        invalid_occurrence_date_times = [None, ""]
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_occurrence_date_time in invalid_occurrence_date_times:
            invalid_json_data["occurrenceDateTime"] = invalid_occurrence_date_time
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_valid_questionnaire_site_code_code(self):
        """
        Test questionnaire_site_code_code validator (code of the Commissioned Healthcare Provider
        who has administered the vaccination) accepts valid site code
        """
        questionnaire_site_code_code = "B0C4P"
        self.assertTrue(
            NHSImmunizationValidators.validate_questionnaire_site_code_code(
                questionnaire_site_code_code
            )
        )

    def test_invalid_questionnaire_site_code_code(self):
        """Test questionnaire_site_code_code validator (code of the Commissioned Healthcare
        Provider who has administered the vaccination) rejects invalid site code
        """
        invalid_questionnaire_site_code_codes = ["urn:12345", "12345", None, ""]
        for questionnaire_site_code_code in invalid_questionnaire_site_code_codes:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_questionnaire_site_code_code(
                    questionnaire_site_code_code
                )

    def test_model_invalid_questionnaire_site_code_code(self):
        """Test validator model rejects invalid questionnaire_site_code_code"""
        invalid_questionnaire_site_code_codes = ["urn:12345", "12345", None, ""]
        invalid_json_data = deepcopy(self.immunization_json_data)
        for (
            invalid_questionnaire_site_code_code
        ) in invalid_questionnaire_site_code_codes:
            invalid_json_data["contained"][0]["item"][0]["answer"][0]["valueCoding"][
                "code"
            ] = invalid_questionnaire_site_code_code
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_valid_identifier_value(self):
        """Test immunization identifier_value validator accepts valid identifier value"""
        identifier_values = [
            "e045626e-4dc5-4df3-bc35-da25263f901e",
            "ACME-vacc123456",
            "ACME-CUSTOMER1-vacc123456",
        ]
        for identifier_value in identifier_values:
            self.assertTrue(
                NHSImmunizationValidators.validate_identifier_value(identifier_value)
            )

    def test_invalid_identifier_value(self):
        """Test immunization identifier_value validator rejects invalid identifier value"""
        invalid_identifier_values = [None, ""]
        for identifier_value in invalid_identifier_values:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_identifier_value(identifier_value)

    def test_model_invalid_identifier_value(self):
        """Test validator model rejects invalid identifier_value"""
        invalid_identifier_values = [None, ""]
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_identifier_value in invalid_identifier_values:
            invalid_json_data["identifier"][0]["value"] = invalid_identifier_value
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)
