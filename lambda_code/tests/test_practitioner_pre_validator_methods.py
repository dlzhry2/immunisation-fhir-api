"""Test practitioner pre-validation methods"""

import unittest
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.practitioner_pre_validators import PractitionerPreValidators


class TestPreractitionerMethodValidators(unittest.TestCase):
    """Test practitioner pre-validation methods"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # set up invalid data types for strings
        cls.invalid_data_types_for_strings = [
            None,
            -1,
            0,
            0.0,
            1,
            True,
            {},
            [],
            {"InvalidKey": "InvalidValue"},
            ["Invalid"],
        ]

        # set up invalid data types for lists
        cls.invalid_data_types_for_lists = [
            None,
            -1,
            0,
            0.0,
            1,
            True,
            {},
            "",
            {"InvalidKey": "InvalidValue"},
            "Invalid",
        ]

        # set up invalid data types for dicts
        cls.invalid_data_types_for_dicts = [
            None,
            -1,
            0,
            0.0,
            1,
            True,
            [],
            "",
            ["Invalid"],
            "Invalid",
        ]
