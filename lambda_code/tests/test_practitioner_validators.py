"""Tests for the NHS Practitioner validators"""

import unittest
import os
import json

from models.fhir_practitioner import PractitionerValidator
from models.nhs_validators import NHSPractitionerValidators


class TestNHSPractitionerValidationRules(unittest.TestCase):
    """Test NHS specific practitioner validation rules"""

    @classmethod
    def setUpClass(cls):
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"
        cls.practitioner_file_path = f"{cls.data_path}/sample_practitioner_event.json"
        with open(cls.practitioner_file_path, "r", encoding="utf-8") as f:
            cls.practitioner_json_data = json.load(f)
        with open(cls.practitioner_file_path, "r", encoding="utf-8") as f:
            cls.untouched_practitioner_json_data = json.load(f)
        cls.practitioner_validator = PractitionerValidator()
        cls.practitioner_validator.add_custom_root_validators()

    def setUp(self):
        """Ensure that good data is not inadvertently amended by the tests"""
        self.assertEqual(
            self.untouched_practitioner_json_data, self.practitioner_json_data
        )

    def test_practitioner_validator(self):
        """Test validator model accepts valid data"""
        self.assertTrue(
            self.practitioner_validator.validate(self.practitioner_json_data)
        )
