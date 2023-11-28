"""Tests for the NHS Immunization validators"""

import unittest
import sys
import os
import json
from copy import deepcopy
import dateutil.parser


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

    def test_immunization_validator(self):
        """Test validator model accepts valid data"""
        self.assertTrue(
            self.immunization_validator.validate(self.immunization_json_data)
        )

    def test_valid_patient_identifier_value(self):
        """Test patient_identifier_value (NHS number) validator accepts valid number"""
        valid_patient_identifier_value = "1234567890"
        self.assertTrue(
            NHSImmunizationValidators.validate_patient_identifier_value(
                valid_patient_identifier_value
            )
        )

    def test_invalid_patient_identifier_value(self):
        """Test patient_identifier_value (NHS number) validator rejects invalid number"""
        invalid_patient_identifier_values = [
            "123456789",
            " 123 5678 ",
            "123 456 789 0 ",
        ]
        for invalid_patient_identifier_value in invalid_patient_identifier_values:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_patient_identifier_value(
                    invalid_patient_identifier_value
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

    def test_valid_occurrence_date_time(self):
        """
        Test occurrence_date_time validator returns valid occurrence date and time in correct
        datetime format
        """
        valid_occurrence_date_times = [
            "2021-01-01",
            "2021-01-01T00:00:00",
            "2021-01-01T00:00:00+00:00",
        ]
        expected_occurrence_date_time = "2021-01-01T00:00:00+00:00"

        for valid_occurrence_date_time in valid_occurrence_date_times:
            returned_occurrence_date_time = (
                NHSImmunizationValidators.validate_occurrence_date_time(
                    dateutil.parser.parse(valid_occurrence_date_time)
                )
            )
            self.assertEqual(
                returned_occurrence_date_time, expected_occurrence_date_time
            )

        # Test unusual timezone
        valid_occurrence_date_time = dateutil.parser.parse("2022-04-05T13:42:11+12:45")
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
        invalid_identifier_values = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_identifier_value in invalid_identifier_values:
            invalid_json_data["identifier"][0]["value"] = invalid_identifier_value
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_valid_identifier_system(self):
        """Test immunization identifier_system validator accepts valid identifier system"""
        identifier_systems = [
            "https://supplierABC/identifiers/vacc",
            "https://supplierABC/ODSCode_ NKO41/identifiers/vacc",
        ]
        for identifier_system in identifier_systems:
            self.assertTrue(
                NHSImmunizationValidators.validate_identifier_system(identifier_system)
            )

    def test_invalid_identifier_system(self):
        """Test immunization identifier_system validator rejects invalid identifier system"""
        invalid_identifier_systems = [None, ""]
        for identifier_system in invalid_identifier_systems:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_identifier_system(identifier_system)

    def test_model_invalid_identifier_system(self):
        """Test validator model rejects invalid identifier_system"""
        invalid_identifier_systems = self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_identifier_system in invalid_identifier_systems:
            invalid_json_data["identifier"][0]["system"] = invalid_identifier_system
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_valid_recorded(self):
        """Test recorded accepts valid recorded (recorded date)"""
        valid_recorded = "2000-01-01"
        self.assertTrue(NHSImmunizationValidators.validate_recorded(valid_recorded))

    def test_invalid_recorded(self):
        """Test recorded rejects invalid recorded (recorded date)"""
        invalid_recordeds = ["2000-13-01", "20001201", None, ""]
        for invalid_recorded in invalid_recordeds:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_recorded(invalid_recorded)

    def test_model_recorded(self):
        """Test validator model rejects invalid recorded (recorded date)"""
        invalid_recordeds = ["2000-13-01", "20010101", 20010101]
        invalid_recordeds += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_recorded in invalid_recordeds:
            invalid_json_data["birthDate"] = invalid_recorded
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_valid_primary_source(self):
        """Test primary_source validator accepts valid primary_source"""
        valid_primary_sources = [True, False]
        for valid_primary_source in valid_primary_sources:
            self.assertEqual(
                NHSImmunizationValidators.validate_primary_source(valid_primary_source),
                valid_primary_source,
            )

    def test_invalid_primary_source(self):
        """Test primary_source validator rejects invalid primary_source"""
        invalid_primary_sources = [-1, 10, "true", "FALSE", None, ""]
        for invalid_primary_source in invalid_primary_sources:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_primary_source(
                    invalid_primary_source
                )

    def test_model_primary_source(self):
        """Test validator model rejects invalid primary_source"""
        invalid_primary_sources = [-1, 10, "True", "FALSE"]
        invalid_primary_sources += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_primary_source in invalid_primary_sources:
            invalid_json_data["primary_source"] = invalid_primary_source
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_valid_status(self):
        """Test status validator accepts valid status"""
        valid_statuses = ["completed", "entered-in-error", "not-done"]
        for valid_status in valid_statuses:
            self.assertTrue(NHSImmunizationValidators.validate_status(valid_status))

    def test_invalid_status(self):
        """Test status validator rejects invalid status"""
        invalid_statuses = [-1, 10, "Invalid Status", None, ""]
        for invalid_status in invalid_statuses:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_status(invalid_status)

    def test_model_status(self):
        """Test validator model rejects invalid status"""
        invalid_statuses = [-1, 10, "Invalid Status"]
        invalid_statuses += self.invalid_data_types_for_mandatory_strings
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_status in invalid_statuses:
            invalid_json_data["status"] = invalid_status
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

    def test_valid_report_origin_text(self):
        """Test report origin text validator accepts valid report origin text"""
        valid_combinations = [
            {"primary_source": "False", "report_origin_text": "Valid text"},
            {"primary_source": "True", "report_origin_text": "Valid text"},
            {"primary_source": "True", "report_origin_text": None},
        ]
        for valid_combination in valid_combinations:
            self.assertEqual(
                NHSImmunizationValidators.validate_report_origin_text(
                    valid_combination["report_origin_text"],
                    valid_combination["primary_source"],
                ),
                valid_combination["report_origin_text"],
            )

    def test_invalid_report_origin_text(self):
        """Test report origin text validator rejects invalid report origin text"""
        invalid_report_origin_texts = [
            """This invalid report origin text is invalid because it has more than 100 characters
            in it, but the maximum number allowed is 100""",
        ]

        # When primary source is true, report origin text is not mandatory unless
        # vaccination was administered in a Primary Care Network
        for invalid_report_origin_text in invalid_report_origin_texts:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_report_origin_text(
                    invalid_report_origin_text, primary_source=True
                )

        # When primary source is false, report origin text is mandatory
        invalid_report_origin_texts += [None, ""]
        for invalid_report_origin_text in invalid_report_origin_texts:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_report_origin_text(
                    invalid_report_origin_text, primary_source=False
                )

    def test_model_valid_report_origin_text(self):
        """Test validator model accepts all valid combinations of report_origin_text
        and primary_source"""
        valid_combinations = [
            {"primary_source": False, "report_origin_text": "Valid text"},
            {"primary_source": True, "report_origin_text": "Valid text"},
        ]
        valid_json_data = deepcopy(self.immunization_json_data)
        for valid_combination in valid_combinations:
            valid_json_data["primarySource"] = valid_combination["primary_source"]
            valid_json_data["reportOrigin"]["text"] = valid_combination[
                "report_origin_text"
            ]
            self.assertTrue(self.immunization_validator.validate(valid_json_data))

        # It is valid, when primary source is true, for report origin text field to be absent
        valid_json_data["primarySource"] = True
        valid_json_data["reportOrigin"].pop("text")
        self.assertTrue(self.immunization_validator.validate(valid_json_data))

    def test_model_invalid_report_origin_text(self):
        """Test validator model rejects all invalid combinations of report_origin_text
        and primary_source"""
        invalid_json_data = deepcopy(self.immunization_json_data)

        # When primary source is true, report origin text is not mandatory unless
        # vaccination was administered in a Primary Care Network
        invalid_json_data["primarySource"] = True
        invalid_report_origin_texts = [
            """This invalid report origin text is invalid because it has more than 100 characters
            in it, but the maximum number allowed is 100""",
        ]
        invalid_json_data = deepcopy(self.immunization_json_data)
        for invalid_report_origin_text in invalid_report_origin_texts:
            invalid_json_data["reportOrigin"]["text"] = invalid_report_origin_text
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

        # When primary source is false, report origin text is mandatory
        invalid_json_data["primarySource"] = False
        invalid_report_origin_texts = [
            """This invalid report origin text is invalid because it has more than 100 characters
            in it, but the maximum number allowed is 100""",
            "",
        ]
        for invalid_report_origin_text in invalid_report_origin_texts:
            invalid_json_data["reportOrigin"]["text"] = invalid_report_origin_text
            with self.assertRaises(ValueError):
                self.immunization_validator.validate(invalid_json_data)

        invalid_json_data["reportOrigin"].pop("text")
        with self.assertRaisesRegex(
            ValueError,
            "REPORT_ORIGIN_TEXT is a mandatory field when PRIMARY_SOURCE is false",
        ):
            self.immunization_validator.validate(invalid_json_data)
