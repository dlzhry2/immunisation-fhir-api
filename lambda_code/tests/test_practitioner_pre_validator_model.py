"""Test practitioner pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy


from models.fhir_practitioner import PractitionerValidator
from .utils import ValidatorModelTests


class TestPractitionerModelPreValidationRules(unittest.TestCase):
    """Test practitioner pre validation rules on the model"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample practitioner event JSON data
        cls.practitioner_file_path = f"{cls.data_path}/sample_practitioner_event.json"
        with open(cls.practitioner_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f)

        # set up the untouched sample practitioner event JSON data
        cls.untouched_practitioner_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = PractitionerValidator()
        cls.validator.add_custom_root_validators()

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_practitioner_json_data, self.json_data)

    def test_model_pre_validate_valid_name(self):
        """Test pre_validate_name accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="name",
            valid_values_to_test=[[{"family": "Test"}]],
        )

    def test_model_pre_validate_invalid_name(self):
        """Test pre_validate_name rejects invalid values when in a model"""
        ValidatorModelTests.list_invalid(
            self,
            field_location="name",
            predefined_list_length=1,
            valid_list_element={"family": "Test"},
        )

    def test_model_pre_validate_valid_name_given(self):
        """Test pre_validate_name_given accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="name[0].given",
            valid_values_to_test=[["Test"], ["Test test"]],
        )

    def test_model_pre_validate_invalid_name_given(self):
        """Test pre_validate_name_given rejects invalid values when in a model"""
        ValidatorModelTests.list_invalid(
            self,
            field_location="name[0].given",
            predefined_list_length=1,
            valid_list_element="Test",
            is_list_of_strings=True,
        )

    def test_model_pre_validate_valid_name_family(self):
        """Test pre_validate_name_family accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="name[0].family",
            valid_values_to_test=["test"],
        )

    def test_model_pre_validate_invalid_name_family(self):
        """Test pre_validate_name_family rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="name[0].family")

    def test_model_pre_validate_valid_identifier(self):
        """Test pre_validate_identifier accepts valid values when in a model"""
        valid_items_to_test = [
            [
                {
                    "system": "https://supplierABC/identifiers/vacc",
                    "value": "ACME-vacc123456",
                }
            ]
        ]

        ValidatorModelTests.valid(
            self,
            field_location="identifier",
            valid_values_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_identifier(self):
        """Test pre_validate_identifier rejects invalid values when in a model"""

        valid_list_element = {
            "system": "https://supplierABC/identifiers/vacc",
            "value": "ACME-vacc123456",
        }

        ValidatorModelTests.list_invalid(
            self,
            field_location="identifier",
            predefined_list_length=1,
            valid_list_element=valid_list_element,
        )

    def test_model_pre_validate_valid_identifier_value(self):
        """Test pre_validate_identifier_value accepts valid values when in a model"""
        valid_items_to_test = [
            "e045626e-4dc5-4df3-bc35-da25263f901e",
            "ACME-vacc123456",
            "ACME-CUSTOMER1-vacc123456",
        ]

        ValidatorModelTests.valid(
            self,
            field_location="identifier[0].value",
            valid_values_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_identifier_value(self):
        """Test pre_validate_identifier_value rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="identifier[0].value")

    def test_model_pre_validate_valid_identifier_system(self):
        """Test pre_validate_identifier_system accepts valid values when in a model"""
        valid_items_to_test = [
            "https://supplierABC/identifiers/vacc",
            "https://supplierABC/ODSCode_NKO41/identifiers/vacc",
        ]

        ValidatorModelTests.valid(
            self,
            field_location="identifier[0].system",
            valid_values_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_identifier_system(self):
        """Test pre_validate_identifier_system rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="identifier[0].system")

    def test_model_pre_validate_valid_identifier_type_coding(self):
        """Test pre_validate_identifier_type_coding accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="identifier[0].type.coding",
            valid_values_to_test=[[{"display": "test_display"}]],
        )

    def test_model_pre_validate_invalid_identifier_type_coding(self):
        """Test pre_validate_identifier_type_coding rejects invalid values when in a model"""
        ValidatorModelTests.list_invalid(
            self,
            field_location="identifier[0].type.coding",
            predefined_list_length=1,
            valid_list_element={"display": "test_display"},
        )

    def test_model_pre_validate_valid_identifier_type_coding_display(self):
        """Test pre_validate_identifier_type_coding_display accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="identifier[0].type.coding[0].display",
            valid_values_to_test=["test"],
        )

    def test_model_pre_validate_invalid_identifier_type_coding_display(self):
        """
        Test pre_validate_identifier_type_coding_display rejects invalid values when in a model
        """
        ValidatorModelTests.string_invalid(
            self, field_location="identifier[0].type.coding[0].display"
        )
