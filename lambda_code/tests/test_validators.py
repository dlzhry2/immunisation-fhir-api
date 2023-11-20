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
from models.nhs_validators import NHSValidators


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

    def setUp(self):
        pass

    def test_nhs_number(self):
        nhs_number = "1234567890"
        self.assertTrue(NHSValidators.validate_nhs_number(nhs_number))

    def test_bad_nhs_number(self):
        bad_nhs_number = "123456789"
        with self.assertRaises(ValueError):
            NHSValidators.validate_nhs_number(bad_nhs_number)

    def test_person_forename(self):
        person_forename = "Valid_forename"
        self.assertTrue(NHSValidators.validate_person_forename(person_forename))

    def test_bad_person_forename(self):
        bad_person_forename = [None, ""]
        for person_forename in bad_person_forename:
            with self.assertRaises(ValueError):
                NHSValidators.validate_person_forename(person_forename)

    def test_person_surname(self):
        person_surname = "Valid_surname"
        self.assertTrue(NHSValidators.validate_person_surname(person_surname))

    def test_bad_person_surname(self):
        bad_person_surname = [None, ""]
        for person_surname in bad_person_surname:
            with self.assertRaises(ValueError):
                NHSValidators.validate_person_surname(person_surname)

    def test_person_dob(self):
        person_dob = "2000-01-01"
        self.assertTrue(NHSValidators.validate_person_dob(person_dob))

    def test_bad_person_dob(self):
        bad_person_dobs = ["2000-13-01", None, ""]
        for dob in bad_person_dobs:
            with self.assertRaises(ValueError):
                NHSValidators.validate_person_dob(dob)

    def test_person_gender_code(self):
        valid_person_gender_codes = ["0", "1", "2", "9"]
        for code in valid_person_gender_codes:
            self.assertTrue(NHSValidators.validate_person_gender_code(code))

    def test_bad_person_gender_code(self):
        invalid_person_gender_codes = [-1, 10, "-1", "10", "BAD_CODE", None, ""]
        for code in invalid_person_gender_codes:
            with self.assertRaises(ValueError):
                NHSValidators.validate_person_gender_code(code)

    def test_person_postcode(self):
        valid_person_postcodes = ["AA00 00AA", "SW1A1AA"]
        for postcode in valid_person_postcodes:
            self.assertTrue(NHSValidators.validate_person_postcode(postcode))

    def test_bad_person_postcode(self):
        invalid_person_postcodes = ["AA000 00AA", "AAA0000AA", None, ""]
        for postcode in invalid_person_postcodes:
            with self.assertRaises(ValueError):
                NHSValidators.validate_person_postcode(postcode)

    def test_date_and_time(self):
        valid_date_and_times = ["2021-01-01T00:00:00+00:00", "2021-01-01", "2021-01-01T00:00:00"]
        expected_date_and_time = datetime.strptime("2021-01-01T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
        for date_and_time in valid_date_and_times:
            actual_date_and_time = NHSValidators.validate_date_and_time(date_and_time)
            self.assertEqual(actual_date_and_time, expected_date_and_time)

        # Test unusual timezone
        valid_date_and_time = "2022-04-05T13:42:11+12:45"
        expected_date_and_time = datetime.strptime("2022-04-05T13:42:11+12:45",
                                                    "%Y-%m-%dT%H:%M:%S%z")
        actual_date_and_time = NHSValidators.validate_date_and_time(valid_date_and_time)
        self.assertEqual(actual_date_and_time, expected_date_and_time)

    def test_bad_date_and_time(self):
        invalid_date_and_times = ["2021-13-01T00:00:00+00:00", "2021-12-01T25:00:00+00:00", 
                                  "2021-12-01T00:00:00+30:00", "Invalid_date_and_time", None, ""]
        for date_and_time in invalid_date_and_times:
            with self.assertRaises(ValueError):
                NHSValidators.validate_date_and_time(date_and_time)

    def test_site_code(self):
        site_code = "B0C4P"
        self.assertTrue(NHSValidators.validate_site_code(site_code))

    def test_bad_site_code(self):
        bad_site_codes = ["urn:12345", None, "", "12345"]
        for site_code in bad_site_codes:
           with self.assertRaises(ValueError):
               NHSValidators.validate_site_code(site_code)

    def test_unique_id(self):
        unique_ids = ["e045626e-4dc5-4df3-bc35-da25263f901e", "ACME-vacc123456", "ACME-CUSTOMER1-vacc123456"]
        for unique_id in unique_ids:
            self.assertTrue(NHSValidators.validate_unique_id(unique_id))

    def test_bad_unique_id(self):
        # TODO: Confirm which ids are acceptable
        bad_unique_ids = ["Bad_unique_id", None, ""]
        for unique_id in bad_unique_ids:
            with self.assertRaises(ValueError):
                NHSValidators.validate_unique_id(unique_id)

    