"""Tests for the validators"""

import unittest
import sys
import os
import json

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_immunization import ImmunizationValidator
from models.fhir_patient import PatientValidator
from models.fhir_practitioner import PractitionerValidator


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
