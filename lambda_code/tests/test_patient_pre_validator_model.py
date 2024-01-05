"""Test patient pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy

from models.fhir_patient import PatientValidator
from .utils import ValidatorModelTests


class TestPatientModelPreValidationRules(unittest.TestCase):
    """Test patient pre validation rules on the model"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample patient event JSON data
        cls.patient_file_path = f"{cls.data_path}/sample_patient_event.json"
        with open(cls.patient_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f)

        # set up the untouched sample patient event JSON data
        cls.untouched_patient_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = PatientValidator()
        cls.validator.add_custom_root_validators()

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_patient_json_data, self.json_data)

    def test_model_pre_validate_name(self):
        """Test pre_validate_name accepts valid values and rejects invalid values when in a model"""
        ValidatorModelTests.test_list_value(
            self,
            field_location="name",
            valid_lists_to_test=[[{"family": "Test"}]],
            predefined_list_length=1,
            valid_list_element={"family": "Test"},
        )

    def test_model_pre_validate_name_given(self):
        """
        Test pre_validate_name_given accepts valid values and rejects invalid values
        when in a model
        """
        ValidatorModelTests.test_list_value(
            self,
            field_location="name[0].given",
            valid_lists_to_test=[["Test"], ["Test test"]],
            predefined_list_length=1,
            valid_list_element="Test",
            is_list_of_strings=True,
        )

    def test_model_pre_validate_name_family(self):
        """
        Test pre_validate_name_family accepts valid values and rejects invalid values
        when in a model
        """
        ValidatorModelTests.test_string_value(
            self, field_location="name[0].family", valid_strings_to_test=["test"]
        )

    def test_model_pre_validate_birth_date(self):
        """
        Test pre_validate_birth_date accepts valid values and rejects invalid values 
        when in a model
        """
        ValidatorModelTests.test_date_value(self, field_location="birthDate")

    def test_model_pre_validate_gender(self):
        """
        Test pre_validate_gender accepts valid values and rejects invalid values 
        when in a model
        """
        invalid_strings_to_test = [
            "0",
            "1",
            "2",
            "9",
            "Male",
            "Female",
            "Unknown",
            "Other",
        ]

        ValidatorModelTests.test_string_value(
            self,
            field_location="gender",
            valid_strings_to_test=["male", "female", "other", "unknown"],
            predefined_values=("male", "female", "other", "unknown"),
            invalid_strings_to_test=invalid_strings_to_test,
        )

    def test_model_pre_validate_address(self):
        """
        Test pre_validate_address accepts valid values and rejects invalid values 
        when in a model
        """
        ValidatorModelTests.test_list_value(
            self,
            field_location="address",
            valid_lists_to_test=[[{"postalCode": "AA1 1AA"}]],
            predefined_list_length=1,
            valid_list_element={"family": "Test"},
        )

    def test_model_pre_validate_address_postal_code(self):
        """
        Test pre_validate_address_postal_code accepts valid values and rejects invalid values 
        when in a model
        """
        # Test invalid data types and empty string
        ValidatorModelTests.test_string_value(
            self,
            field_location="address[0].postalCode",
            valid_strings_to_test=["AA00 00AA", "A0 0AA"],
            is_postal_code=True,
        )
