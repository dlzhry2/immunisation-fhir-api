"""Tests for the validators"""

import unittest
import sys
import os
import json
from datetime import datetime

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_immunization import ImmunizationValidator
from models.fhir_patient import PatientValidator
from models.fhir_practitioner import PractitionerValidator
from models.nhs_validators import (
    NHSImmunizationValidators,
    NHSPatientValidators,
    NHSPractitionerValidators,
)


class TestValidators(unittest.TestCase):
    """Basic tests for the validators. In depth tests TBA"""

    def setUp(self) -> None:
        self.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"
        self.immunization_file_path = f"{self.data_path}/sample_immunization_event.json"
        with open(self.immunization_file_path, "r", encoding="utf-8") as f:
            self.immunization_json_data = json.load(f)

        self.patient_file_path = f"{self.data_path}/sample_patient_event.json"
        with open(self.patient_file_path, "r", encoding="utf-8") as f:
            self.patient_json_data = json.load(f)

        self.practitioner_file_path = f"{self.data_path}/sample_practitioner_event.json"
        with open(self.practitioner_file_path, "r", encoding="utf-8") as f:
            self.practitioner_json_data = json.load(f)

    def test_immunization_validator(self):
        """Test the ImmunizationValidator""" ""
        immunization_validator = ImmunizationValidator(self.immunization_json_data)
        self.assertTrue(immunization_validator.validate())

    def test_patient_validator(self):
        """Test the PatientValidator"""
        patient_validator = PatientValidator(self.patient_json_data)
        self.assertTrue(patient_validator.validate())

    def test_practitioner_validator(self):
        """Test the PractitionerValidator"""
        practitioner_validator = PractitionerValidator(self.practitioner_json_data)
        self.assertTrue(practitioner_validator.validate())


class TestNHSValidationRules(unittest.TestCase):
    """Test NHS specific validation rules"""

    def setUp(self):
        pass

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
        valid_genders = ["0", "1", "2", "9"]
        for valid_gender in valid_genders:
            self.assertTrue(NHSPatientValidators.validate_gender(valid_gender))

    def test_invalid_gender(self):
        """Test gender validator rejects invalid gender"""
        invalid_genders = [-1, 10, "-1", "10", "Male", "Unknown", None, ""]
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

    def test_valid_unique_id(self):
        """Test unique_id validator accepts valid unique id"""
        unique_ids = [
            "e045626e-4dc5-4df3-bc35-da25263f901e",
            "ACME-vacc123456",
            "ACME-CUSTOMER1-vacc123456",
        ]
        for unique_id in unique_ids:
            self.assertTrue(NHSImmunizationValidators.validate_unique_id(unique_id))

    def test_invalid_unique_id(self):
        """Test unique_id validator rejects invalid unique id"""
        invalid_unique_ids = [None, ""]
        for unique_id in invalid_unique_ids:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_unique_id(unique_id)
