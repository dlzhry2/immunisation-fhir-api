"""Test immunization pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from decimal import Decimal

from models.fhir_immunization import ImmunizationValidator
from .utils import (
    generate_field_location_for_extension,
    # these have an underscore to avoid pytest collecting them as tests
    test_valid_values_accepted as _test_valid_values_accepted,
    test_invalid_values_rejected as _test_invalid_values_rejected,
    test_missing_mandatory_field_rejected as _test_missing_mandatory_field_rejected,
)


class TestImmunizationModelPostValidationRules(unittest.TestCase):
    """Test immunization post validation rules on the FHIR model"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample immunization event JSON data
        cls.immunization_file_path = f"{cls.data_path}/sample_immunization_event.json"
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f, parse_float=Decimal)

        # set up the untouched sample immunization event JSON data
        cls.untouched_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = ImmunizationValidator()
        cls.validator.add_custom_root_pre_validators()
        cls.validator.add_custom_root_post_validators()

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_json_data, self.json_data)

    def test_model_post_reduce_validation_code(self):
        """
        Test reduce_validation_code accepts valid values and rejects invalid values
        """
        field_location = "reduce_validation_code"

    def test_model_post_vaccination_procedure_code(self):
        """
        Test post_vaccination_procedure_code accepts valid values and rejects invalid values
        """
        url = (
            "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "VaccinationProcedure"
        )
        field_location = generate_field_location_for_extension(url, "code")

        _test_valid_values_accepted(
            self,
            valid_json_data=self.json_data,
            field_location=field_location,
            valid_values_to_test=["1324681000000101"],
        )
        _test_invalid_values_rejected(
            self,
            valid_json_data=self.json_data,
            field_location=field_location,
            invalid_value="INVALID_VALUE",
            expected_error_message=f"{field_location}:"
            + " INVALID_VALUE is not a valid code for this service",
            expected_error_type="value_error",
        )
        _test_missing_mandatory_field_rejected(
            self,
            valid_json_data=self.json_data,
            field_location=field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )
