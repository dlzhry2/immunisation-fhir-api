"""Test patient pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from pydantic import ValidationError


from models.fhir_patient import PatientValidator
from ..tests.utils import (
    InvalidDataTypes,
    GenericValidatorModelTests,
)


class TestPatientModelPreValidationRules(unittest.TestCase):
    """
    Test patient pre validation rules on the model

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

        # set up the sample patient event JSON data
        cls.patient_file_path = f"{cls.data_path}/sample_patient_event.json"
        with open(cls.patient_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f)

        # set up the untouched sample patient event JSON data
        cls.untouched_patient_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = PatientValidator()
        cls.validator.add_custom_root_validators()

        # set up invalid data types for strings
        cls.invalid_data_types_for_strings = InvalidDataTypes.for_strings

        # set up invalid data types for lists
        cls.invalid_data_types_for_lists = InvalidDataTypes.for_lists

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_patient_json_data, self.json_data)

    def test_model_pre_validate_valid_name(self):
        """Test pre_validate_name accepts valid values when in a model"""
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["name"],
            valid_items_to_test=[[{"family": "Test"}]],
        )

    def test_model_pre_validate_invalid_name(self):
        """Test pre_validate_name rejects invalid values when in a model"""
        invalid_list_lengths_to_test = [[{"family": "Test"}, {"family": "Test"}]]

        GenericValidatorModelTests.list_invalid(
            self,
            field_location="name",
            keys_to_access_value=["name"],
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_list_lengths_to_test,
        )

    def test_model_pre_validate_valid_name_given(self):
        """Test pre_validate_name_given accepts valid values when in a model"""
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["name", 0, "given"],
            valid_items_to_test=[["Test"], ["Test1", "Test2"]],
        )

    def test_model_pre_validate_invalid_name_given(self):
        """Test pre_validate_name_given rejects invalid values when in a model"""
        invalid_lists = [
            [1, "test"],
            ["test", False],
            [["Test1"]],
        ]

        GenericValidatorModelTests.list_invalid(
            self,
            field_location="name[0] -> given",
            keys_to_access_value=["name", 0, "given"],
            invalid_lists_with_non_string_data_types_to_test=invalid_lists,
        )

    def test_model_pre_validate_valid_name_family(self):
        """Test pre_validate_name_family accepts valid values when in a model"""
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["name", 0, "family"],
            valid_items_to_test=["test"],
        )

    def test_model_pre_validate_invalid_name_family(self):
        """Test pre_validate_name_family rejects invalid values when in a model"""
        GenericValidatorModelTests.string_invalid(
            self,
            field_location="name[0] -> family",
            keys_to_access_value=["name", 0, "family"],
        )

    def test_model_pre_validate_valid_birth_date(self):
        """Test pre_validate_birth_date accepts valid values when in a model"""
        valid_birth_dates = ["2000-01-01", "1933-12-31"]
        valid_json_data = deepcopy(self.json_data)
        for valid_birth_date in valid_birth_dates:
            valid_json_data["birthDate"] = valid_birth_date
            self.assertTrue(self.validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_birth_date(self):
        """Test pre_validate_birth_date rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["birthDate"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "birthDate must be a string (type=type_error)" in str(error.exception)
            )

        # Test invalid string formats
        invalid_birth_dates = [
            "",
            "invalid",
            "20000101",
            "2000-01-011",
            "12000-01-01",
            "12000-01-021",
            "99-01-01",
            "01-01-99",
            "01-01-2000",
        ]

        for invalid_birth_date in invalid_birth_dates:
            invalid_json_data["birthDate"] = invalid_birth_date

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                'birthDate must be a string in the format "YYYY-MM-DD" (type=value_error)'
                in str(error.exception)
            )

        # Test invalid dates
        invalid_birth_dates = [
            "2000-00-01",
            "2000-13-01",
            "2000-01-00",
            "2000-01-32",
            "2000-02-30",
        ]

        for invalid_birth_date in invalid_birth_dates:
            invalid_json_data["birthDate"] = invalid_birth_date

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "birthDate must be a valid date (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_gender(self):
        """Test pre_validate_gender accepts valid values when in a model"""
        valid_genders = ["male", "female", "other", "unknown"]
        valid_json_data = deepcopy(self.json_data)
        for valid_gender in valid_genders:
            valid_json_data["gender"] = valid_gender
            self.assertTrue(self.validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_gender(self):
        """Test pre_validate_gender rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["gender"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "gender must be a string (type=type_error)" in str(error.exception)
            )

        # Test empty string
        invalid_json_data["gender"] = ""
        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.validator.validate(invalid_json_data)

        self.assertTrue(
            "gender must be a non-empty string (type=value_error)"
            in str(error.exception)
        )

        # Test invalid string formats
        invalid_genders = [
            "0",
            "1",
            "2",
            "9",
            "Male",
            "Female",
            "Unknown",
            "Other",
        ]

        for invalid_gender in invalid_genders:
            invalid_json_data["gender"] = invalid_gender

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "gender must be one of the following: "
                + "male, female, other, unknown (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_address(self):
        """Test pre_validate_address accepts valid values when in a model"""
        valid_address = [{"postalCode": "AA1 1AA"}]
        valid_json_data = deepcopy(self.json_data)
        valid_json_data["address"] = valid_address

        self.assertTrue(self.validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_address(self):
        """Test pre_validate_address rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.json_data)

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            invalid_json_data["address"] = invalid_data_type_for_list

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "address must be an array (type=type_error)" in str(error.exception)
            )

        # Test invalid list lengths
        invalid_addresses = [[], [{"family": "Test"}, {"family": "Test"}]]
        for invalid_address in invalid_addresses:
            invalid_json_data["address"] = invalid_address

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "address must be an array of length 1 (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_address_postal_code(self):
        """Test pre_validate_address_postal_code accepts valid values when in a model"""
        valid_address_postal_codes = ["AA00 00AA", "A0 0AA"]
        valid_json_data = deepcopy(self.json_data)
        for valid_address_postal_code in valid_address_postal_codes:
            valid_json_data["address"][0]["postalCode"] = valid_address_postal_code
            self.assertTrue(self.validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_address_postal_code(self):
        """Test pre_validate_address_postal_code rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["address"][0]["postalCode"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "address -> postalCode must be a string (type=type_error)"
                in str(error.exception)
            )

        # Test empty string
        invalid_json_data["address"][0]["postalCode"] = ""
        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.validator.validate(invalid_json_data)

        self.assertTrue(
            "address -> postalCode must be a non-empty string (type=value_error)"
            in str(error.exception)
        )

        # Test address_postal_code which are not separated into the two parts by a single space
        invalid_address_postal_codes = [
            "SW1  1AA",
            "SW 1 1A",
            "AAA0000AA",
            "SW11AA",
        ]

        for invalid_address_postal_code in invalid_address_postal_codes:
            invalid_json_data["address"][0]["postalCode"] = invalid_address_postal_code

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "address -> postalCode must contain a single space, which divides the two parts of the postal code (type=value_error)"
                in str(error.exception)
            )

        # Test invalid address_postal_code length
        invalid_json_data["address"][0]["postalCode"] = "AA000 00AA"

        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.validator.validate(invalid_json_data)

        self.assertTrue(
            "address -> postalCode must be 8 or fewer characters (excluding spaces) (type=value_error)"
            in str(error.exception)
        )
