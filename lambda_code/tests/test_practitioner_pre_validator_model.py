"""Test practitioner pre validation rules on the model"""
import unittest
import sys
import os
import json
from copy import deepcopy

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_practitioner import PractitionerValidator


class TestPractitionerModelPreValidationRules(unittest.TestCase):
    """
    Test practitioner pre validation rules on the model

    Notes:-
    TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
    this happens, the error message is suffixed with the type of error e.g. type_error or
    value_error. This is why the tests check for the type of error in the error message.

    """

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample practitioner event JSON data
        cls.practitioner_file_path = f"{cls.data_path}/sample_practitioner_event.json"
        with open(cls.practitioner_file_path, "r", encoding="utf-8") as f:
            cls.practitioner_json_data = json.load(f)

        # set up the untouched sample practitioner event JSON data
        cls.untouched_practitioner_json_data = deepcopy(cls.practitioner_json_data)

        # set up the validator and add custom root validators
        cls.practitioner_validator = PractitionerValidator()
        cls.practitioner_validator.add_custom_root_validators()

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
            (),
            {"InvalidKey": "InvalidValue"},
            ["Invalid"],
            ("Invalid1", "Invalid2"),
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

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(
            self.untouched_practitioner_json_data, self.practitioner_json_data
        )
