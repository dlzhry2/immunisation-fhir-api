"""Tests for the NHS Immunization model validators"""

import unittest
import sys
import os
import json
from copy import deepcopy


sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_immunization import ImmunizationValidator


class TestNHSImmunizationModelValidationRules(unittest.TestCase):
    """Test NHS specific immunization validation rules on the model"""

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
            self.untouched_immunization_json_data, self.immunization_json_data
        )

    def test_model_immunization_validator(self):
        """Test validator model accepts valid data"""
        self.assertTrue(
            self.immunization_validator.validate(self.immunization_json_data)
        )

    def test_model_valid_patient_identifier_value(self):
        """Test validator model accepts all acceptable patient_identifier_value formats"""
        valid_patient_identifier_values = ["1234567890", None]
        valid_json_data = deepcopy(self.immunization_json_data)
        for valid_patient_identifier_value in valid_patient_identifier_values:
            valid_json_data["patient"]["identifier"][
                "value"
            ] = valid_patient_identifier_value
            self.assertTrue(self.immunization_validator.validate(valid_json_data))

    def test_model_invalid_patient_identifier_value(self):
        """Test validator model rejects invalid patient_identifier_value"""
        invalid_json_data = deepcopy(self.immunization_json_data)
        invalid_patient_identifier_values = [
            "123456789",
            " 123 5678 ",
            "123 456 789 0 ",
            ["1234567890"],
        ]
        for invalid_patient_identifier_value in invalid_patient_identifier_values:
            invalid_json_data["patient"]["identifier"][
                "value"
            ] = invalid_patient_identifier_value
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_valid_occurence_date_time(self):
        """Test validator model accepts all acceptable occurence_date_time formats"""
        valid_occurrence_date_times = [
            "2021-01-01",
            "2021-01-01T00:00:00",
            "2021-01-01T00:00:00+00:00",
            "2022-04-05T13:42:11+12:45",
        ]
        valid_json_data = deepcopy(self.immunization_json_data)
        for valid_occurrence_date_time in valid_occurrence_date_times:
            valid_json_data["occurrenceDateTime"] = valid_occurrence_date_time
            self.assertTrue(self.immunization_validator.validate(valid_json_data))

    def test_model_invalid_occurrence_date_time(self):
        """Test validator model rejects invalid occurrence_date_time"""
        invalid_occurrence_date_times = [None, "", 123456, "20000101"]
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_occurrence_date_time in invalid_occurrence_date_times:
            invalid_json_data["occurrenceDateTime"] = invalid_occurrence_date_time
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_invalid_questionnaire_site_code_code(self):
        """Test validator model rejects invalid questionnaire_site_code_code"""
        invalid_questionnaire_site_code_codes = ["urn:12345", "12345"]
        invalid_questionnaire_site_code_codes += (
            self.invalid_data_types_for_mandatory_strings
        )
        invalid_json_data = deepcopy(self.immunization_json_data)
        for (
            invalid_questionnaire_site_code_code
        ) in invalid_questionnaire_site_code_codes:
            invalid_json_data["contained"][0]["item"][0]["answer"][0]["valueCoding"][
                "code"
            ] = invalid_questionnaire_site_code_code
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_invalid_identifier_value(self):
        """Test validator model rejects invalid identifier_value"""
        invalid_identifier_values = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_identifier_value in invalid_identifier_values:
            invalid_json_data["identifier"][0]["value"] = invalid_identifier_value
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_invalid_identifier_system(self):
        """Test validator model rejects invalid identifier_system"""
        invalid_identifier_systems = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_identifier_system in invalid_identifier_systems:
            invalid_json_data["identifier"][0]["system"] = invalid_identifier_system
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_invalid_recorded(self):
        """Test validator model rejects invalid recorded (recorded date)"""
        invalid_recordeds = ["2000-13-01", "20010101", 20010101]
        invalid_recordeds += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_recorded in invalid_recordeds:
            invalid_json_data["birthDate"] = invalid_recorded
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_invalid_primary_source(self):
        """Test validator model rejects invalid primary_source"""
        invalid_primary_sources = [-1, 10, "True", "FALSE"]
        invalid_primary_sources += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_primary_source in invalid_primary_sources:
            invalid_json_data["primary_source"] = invalid_primary_source
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_invalid_status(self):
        """Test validator model rejects invalid status"""
        invalid_statuses = [-1, 10, "Invalid Status"]
        invalid_statuses += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_status in invalid_statuses:
            invalid_json_data["status"] = invalid_status
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_valid_report_origin_text_when_primary_source_true(self):
        """Test validator model accepts valid report_origin_text
        when primary_source is true"""
        valid_json_data = deepcopy(self.immunization_json_data)
        valid_json_data["primarySource"] = True

        valid_json_data["reportOrigin"]["text"] = "Valid text"
        self.assertTrue(self.immunization_validator.validate(valid_json_data))

        # It is also valid (if the vaccine wasn't administered in a primary care network)
        #  for report origin text field to be absent
        valid_json_data["reportOrigin"].pop("text")
        self.assertTrue(self.immunization_validator.validate(valid_json_data))

    def test_model_valid_report_origin_text_when_primary_source_false(self):
        """Test validator model accepts valid report_origin_text
        when primary_source is false"""
        valid_json_data = deepcopy(self.immunization_json_data)
        valid_json_data["primarySource"] = False
        valid_json_data["reportOrigin"]["text"] = "Valid text"
        self.assertTrue(self.immunization_validator.validate(valid_json_data))

    def test_model_invalid_report_origin_text_when_primary_source_true(self):
        """Test validator model rejects invalid report_origin_text
        when primary_source is true"""
        invalid_json_data = deepcopy(self.immunization_json_data)
        invalid_json_data["primarySource"] = True
        invalid_report_origin_texts = [
            """This invalid report origin text is invalid because it has more than 100 characters
            in it, but the maximum number allowed is 100""",
        ]
        for invalid_report_origin_text in invalid_report_origin_texts:
            invalid_json_data["reportOrigin"]["text"] = invalid_report_origin_text
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_model_invalid_report_origin_text_when_primary_source_false(self):
        """Test validator model rejects invalid report_origin_text
        when primary_source is true"""
        # When primary source is false, report origin text is mandatory
        invalid_json_data = deepcopy(self.immunization_json_data)
        invalid_json_data["primarySource"] = False

        invalid_report_origin_texts = [
            """This invalid report origin text is invalid because it has more than 100 characters
                in it, but the maximum number allowed is 100"""
        ]
        for invalid_report_origin_text in invalid_report_origin_texts:
            invalid_json_data["reportOrigin"]["text"] = invalid_report_origin_text
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

        invalid_json_data["reportOrigin"].pop("text")
        error = (
            "REPORT_ORIGIN_TEXT is a mandatory field, and must be a non-empty string,",
            "when PRIMARY_SOURCE is false",
        )
        with self.assertRaisesRegex(
            ValueError,
            " ".join(error),
        ):
            self.immunization_validator.validate(invalid_json_data)
