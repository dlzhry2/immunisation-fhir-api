"""Tests for the utils module"""

import unittest
from copy import deepcopy
from models.utils.generic_utils import nhs_number_mod11_check, get_nhs_number_verification_status_code
from .utils.generic_utils import load_json_data


class UtilsTests(unittest.TestCase):
    """Tests for models.utils.generic_utils module"""

    @classmethod
    def setUpClass(cls):
        cls.json_data = load_json_data("sample_covid_immunization_event.json")

    def test_nhs_number_mod11_check(self):
        """Test the nhs_number_mod11_check function"""
        # All of these NHS numbers are valid
        valid_nhs_numbers = [
            "1345678940",  # check digit 11 is 0
            "9990548609",  # PDS example with 0's in the middle
            "9693821998",  # regular example from PDS
        ]

        for valid_nhs_number in valid_nhs_numbers:
            self.assertTrue(nhs_number_mod11_check(valid_nhs_number))

        invalid_nhs_numbers = [
            "9434765911",  # check digit 1 doesn't match result (9)
            "1234567890",  # check digit 10
            "234567890",  # nhs_number too short
            "12345678901",  # nhs_number too long
            "A234567890",  # nhs_number contains non-numeric characters
        ]

        for invalid_nhs_number in invalid_nhs_numbers:
            self.assertFalse(nhs_number_mod11_check(invalid_nhs_number))
