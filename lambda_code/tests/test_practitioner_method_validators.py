"""Tests for the NHS Practitioner method validators"""

import unittest
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.nhs_validators import NHSPractitionerValidators


class TestNHSPractitionerValidationRules(unittest.TestCase):
    """Test NHS specific practitioner validation rules"""

    @classmethod
    def setUpClass(cls):
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
