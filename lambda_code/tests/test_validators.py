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

    def test_valid_nhs_number(self):
        """Test nhs_number validator accepts valid nhs number"""
        valid_nhs_numbers = ["1234567890", " 12345 67890 "]
        for valid_nhs_number in valid_nhs_numbers:
            self.assertTrue(
                NHSImmunizationValidators.validate_nhs_number(valid_nhs_number)
            )

    def test_invalid_nhs_number(self):
        """Test nhs_number validator rejects invalid nhs number"""
        invalid_nhs_number = "123456789"
        with self.assertRaises(ValueError):
            NHSImmunizationValidators.validate_nhs_number(invalid_nhs_number)

    def test_valid_person_forename(self):
        """Test person_forename validator accepts valid person forename"""
        valid_person_forename = "Valid_forename"
        self.assertTrue(
            NHSPatientValidators.validate_person_forename(valid_person_forename)
        )

    def test_invalid_person_forename(self):
        """Test person_forname validator rejects invalid person forename"""
        invalid_person_forenames = [None, ""]
        for invalid_person_forename in invalid_person_forenames:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_person_forename(invalid_person_forename)

    def test_valid_person_surname(self):
        """Test person_surname validator accepts valid person surname"""
        valid_person_surname = "Valid_surname"
        self.assertTrue(
            NHSPatientValidators.validate_person_surname(valid_person_surname)
        )

    def test_invalid_person_surname(self):
        """Test person_forname validator rejects invalid patient surname"""
        invalid_person_surnames = [None, ""]
        for invalid_person_surname in invalid_person_surnames:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_person_surname(invalid_person_surname)

    def test_person_dob(self):
        """Test person_dob accepts valid person DOB"""
        valid_person_dob = "2000-01-01"
        self.assertTrue(NHSPatientValidators.validate_person_dob(valid_person_dob))

    def test_invalid_person_dob(self):
        """Test person_dob rejects invalid person DOB"""
        invalid_person_dobs = ["2000-13-01", "20001201", None, ""]
        for invalid_person_dob in invalid_person_dobs:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_person_dob(invalid_person_dob)

    def test_person_gender_code(self):
        """Test person_gender_code validator accepts valid person gender code"""
        valid_person_gender_codes = ["0", "1", "2", "9"]
        for valid_person_gender_code in valid_person_gender_codes:
            self.assertTrue(
                NHSPatientValidators.validate_person_gender_code(
                    valid_person_gender_code
                )
            )

    def test_invalid_person_gender_code(self):
        """Test person_gender_code validator rejects invalid person gender codes"""
        invalid_person_gender_codes = [-1, 10, "-1", "10", "invalid_CODE", None, ""]
        for invalid_person_gender_code in invalid_person_gender_codes:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_person_gender_code(
                    invalid_person_gender_code
                )

    def test_person_postcode(self):
        """Test person_postcode validator accepts valid person postcode"""
        valid_person_postcodes = ["AA00 00AA", "A0 0AA"]
        for valid_person_postcode in valid_person_postcodes:
            self.assertTrue(
                NHSPatientValidators.validate_person_postcode(valid_person_postcode)
            )

    def test_invalid_person_postcode(self):
        """Test person_postcode validator rejects invalid person postcode"""
        invalid_person_postcodes = [
            "AA000 00AA",
            "SW1  1AA",
            "SW 1 1A",
            "AAA0000AA",
            "SW11AA",
            None,
            "",
        ]
        for invalid_person_postcode in invalid_person_postcodes:
            with self.assertRaises(ValueError):
                NHSPatientValidators.validate_person_postcode(invalid_person_postcode)

    def test_date_and_time(self):
        """ "Test date_and_time validator returns valid date and time in correct datetime format"""
        valid_date_and_times = [
            datetime.strptime("2021-01-01", "%Y-%m-%d"),
            datetime.strptime("2021-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
            datetime.strptime("2021-01-01T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
        ]
        expected_date_and_time = "2021-01-01T00:00:00+00:00"

        for valid_date_and_time in valid_date_and_times:
            returned_date_and_time = NHSImmunizationValidators.validate_date_and_time(
                valid_date_and_time
            )
            self.assertEqual(returned_date_and_time, expected_date_and_time)

        # Test unusual timezone
        valid_date_and_time = datetime.strptime(
            "2022-04-05T13:42:11+12:45", "%Y-%m-%dT%H:%M:%S%z"
        )
        expected_date_and_time = "2022-04-05T13:42:11+12:45"
        returned_date_and_time = NHSImmunizationValidators.validate_date_and_time(
            valid_date_and_time
        )
        self.assertEqual(returned_date_and_time, expected_date_and_time)

    def test_invalid_date_and_time(self):
        """Test date_and_time validator rejects invalid date and time"""
        invalid_date_and_times = [None, ""]
        for invalid_date_and_time in invalid_date_and_times:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_date_and_time(invalid_date_and_time)

    def test_site_code(self):
        """Test site_code validator accepts valid site code"""
        site_code = "B0C4P"
        self.assertTrue(NHSImmunizationValidators.validate_site_code(site_code))

    def test_invalid_site_code(self):
        """Test site_code validator rejects invalid site code"""
        invalid_site_codes = ["urn:12345", "12345", None, ""]
        for site_code in invalid_site_codes:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_site_code(site_code)

    def test_unique_id(self):
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
        # TODO: Confirm which ids are acceptable
        invalid_unique_ids = ["invalid_unique_id", None, ""]
        for unique_id in invalid_unique_ids:
            with self.assertRaises(ValueError):
                NHSImmunizationValidators.validate_unique_id(unique_id)
