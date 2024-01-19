"""Test immunization pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from decimal import Decimal

from models.fhir_immunization import ImmunizationValidator
from .utils import (
    generate_field_location_for_extension,
    generate_field_location_for_questionnnaire_response,
    # these have an underscore to avoid pytest collecting them as tests
    test_valid_values_accepted as _test_valid_values_accepted,
    test_invalid_values_rejected as _test_invalid_values_rejected,
    test_missing_mandatory_field_rejected as _test_missing_mandatory_field_rejected,
)
from jsonpath_ng.ext import parse


class TestImmunizationModelPostValidationRules(unittest.TestCase):
    """Test immunization post validation rules on the FHIR model"""

    @classmethod
    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Set up the path for the sample data
        self.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample immunization event JSON data
        self.immunization_file_path = f"{self.data_path}/sample_immunization_event.json"
        with open(self.immunization_file_path, "r", encoding="utf-8") as f:
            self.json_data = json.load(f, parse_float=Decimal)

        # set up the validator and add custom root validators
        self.validator = ImmunizationValidator()
        self.validator.add_custom_root_pre_validators()
        self.validator.add_custom_root_post_validators()

    def test_model_post_reduce_validation_code(self):
        """
        Test reduce_validation_code accepts valid values and rejects invalid values
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = generate_field_location_for_questionnnaire_response(
            link_id="ReduceValidation", field_type="code"
        )

        # Test that reduce_validation_code property is to the value of
        # reduce_validation_code in the JSON data, where it exists
        for valid_value in ["True", "False"]:
            valid_json_data = parse(field_location).update(valid_json_data, valid_value)
            self.validator.validate(valid_json_data)
            self.assertEqual(
                valid_value, self.validator.immunization.reduce_validation_code
            )

        # Test that reduce_validation_code property is set as False, when there is no
        # reduce_validation_code in the JSON data
        valid_json_data = parse(field_location).filter(lambda d: True, valid_json_data)
        self.validator.validate(valid_json_data)
        self.assertEqual("False", self.validator.immunization.reduce_validation_code)

    def test_model_post_vaccination_procedure_code(self):
        """
        Test post_vaccination_procedure_code accepts valid values and rejects invalid values
        """
        url = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure"
        field_location = generate_field_location_for_extension(url, "code")

        # Test that a valid COVID-19 code is accepted and vaccine_type is therefore set to COVID-19
        _test_valid_values_accepted(
            self,
            valid_json_data=self.json_data,
            field_location=field_location,
            valid_values_to_test=["1324681000000101"],
        )
        self.assertEqual("COVID-19", self.validator.immunization.vaccine_type)

        # Test that an invalid code is rejected
        _test_invalid_values_rejected(
            self,
            valid_json_data=self.json_data,
            field_location=field_location,
            invalid_value="INVALID_VALUE",
            expected_error_message=f"{field_location}:"
            + " INVALID_VALUE is not a valid code for this service",
            expected_error_type="value_error",
        )

        # Test that json data which doesn't contain vaccination_procedure_code is rejected
        _test_missing_mandatory_field_rejected(
            self,
            valid_json_data=self.json_data,
            field_location=field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )
