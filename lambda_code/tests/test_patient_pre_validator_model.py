"""Test patient pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from pydantic import ValidationError


from models.fhir_patient import PatientValidator


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
            cls.patient_json_data = json.load(f)

        # set up the untouched sample patient event JSON data
        cls.untouched_patient_json_data = deepcopy(cls.patient_json_data)

        # set up the validator and add custom root validators
        cls.patient_validator = PatientValidator()
        cls.patient_validator.add_custom_root_validators()

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
        self.assertEqual(self.untouched_patient_json_data, self.patient_json_data)

    def test_model_pre_validate_valid_name(self):
        """Test pre_validate_name accepts valid values when in a model"""
        valid_name = [{"family": "Test"}]
        valid_json_data = deepcopy(self.patient_json_data)
        valid_json_data["name"] = valid_name

        self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_name(self):
        """Test pre_validate_name rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.patient_json_data)

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            invalid_json_data["name"] = invalid_data_type_for_list

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "name must be an array (type=type_error)" in str(error.exception)
            )

        # Test invalid list lengths
        invalid_names = [[], [{"family": "Test"}, {"family": "Test"}]]
        for invalid_name in invalid_names:
            invalid_json_data["name"] = invalid_name

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "name must be an array of length 1 (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_name_given(self):
        """Test pre_validate_name_given accepts valid values when in a model"""
        valid_names_given = [["Test"], ["Test1", "Test2"]]
        valid_json_data = deepcopy(self.patient_json_data)
        for valid_name_given in valid_names_given:
            valid_json_data["name"][0]["given"] = valid_name_given
            self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_name_given(self):
        """Test pre_validate_name_given rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.patient_json_data)

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            invalid_json_data["name"][0]["given"] = invalid_data_type_for_list

            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "name -> given must be an array (type=type_error)"
                in str(error.exception)
            )

        # Test empty list is invalid
        invalid_json_data["name"][0]["given"] = []

        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.patient_validator.validate(invalid_json_data)

        self.assertTrue(
            "name -> given must be a non-empty array (type=value_error)"
            in str(error.exception)
        )

        # Test invalid data types for list items
        invalid_names_given = [[1, "test"], ["test", False], [["Test1"]]]
        for invalid_name_given in invalid_names_given:
            invalid_json_data["name"][0]["given"] = invalid_name_given

            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "name -> given must be an array of strings (type=type_error)"
                in str(error.exception)
            )

        # Test invalid string (empty) in list
        invalid_json_data["name"][0]["given"] = [""]

        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.patient_validator.validate(invalid_json_data)

        self.assertTrue(
            "name -> given must be an array of non-empty strings (type=value_error)"
            in str(error.exception)
        )

    def test_model_pre_validate_valid_name_family(self):
        """Test pre_validate_name_family accepts valid values when in a model"""
        valid_name_family = "test"
        valid_json_data = deepcopy(self.patient_json_data)
        valid_json_data["name"][0]["family"] = valid_name_family
        self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_name_family(self):
        """Test pre_validate_name_family rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.patient_json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["name"][0]["family"] = invalid_data_type_for_string

            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "name -> family must be a string (type=type_error)"
                in str(error.exception)
            )

        # Test empty string is invalid
        invalid_json_data["name"][0]["family"] = ""

        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.patient_validator.validate(invalid_json_data)

        self.assertTrue(
            "name -> family must be a non-empty string (type=value_error)"
            in str(error.exception)
        )

    def test_model_pre_validate_valid_birth_date(self):
        """Test pre_validate_birth_date accepts valid values when in a model"""
        valid_birth_dates = ["2000-01-01", "1933-12-31"]
        valid_json_data = deepcopy(self.patient_json_data)
        for valid_birth_date in valid_birth_dates:
            valid_json_data["birthDate"] = valid_birth_date
            self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_birth_date(self):
        """Test pre_validate_birth_date rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.patient_json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["birthDate"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

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
                self.patient_validator.validate(invalid_json_data)

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
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "birthDate must be a valid date (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_gender(self):
        """Test pre_validate_gender accepts valid values when in a model"""
        valid_genders = ["male", "female", "other", "unknown"]
        valid_json_data = deepcopy(self.patient_json_data)
        for valid_gender in valid_genders:
            valid_json_data["gender"] = valid_gender
            self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_gender(self):
        """Test pre_validate_gender rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.patient_json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["gender"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "gender must be a string (type=type_error)" in str(error.exception)
            )

        # Test empty string
        invalid_json_data["gender"] = ""
        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.patient_validator.validate(invalid_json_data)

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
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "gender must be one of the following: "
                + "male, female, other, unknown (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_address(self):
        """Test pre_validate_address accepts valid values when in a model"""
        valid_address = [{"postalCode": "AA1 1AA"}]
        valid_json_data = deepcopy(self.patient_json_data)
        valid_json_data["address"] = valid_address

        self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_address(self):
        """Test pre_validate_address rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.patient_json_data)

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            invalid_json_data["address"] = invalid_data_type_for_list

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "address must be an array (type=type_error)" in str(error.exception)
            )

        # Test invalid list lengths
        invalid_addresses = [[], [{"family": "Test"}, {"family": "Test"}]]
        for invalid_address in invalid_addresses:
            invalid_json_data["address"] = invalid_address

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "address must be an array of length 1 (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_address_postal_code(self):
        """Test pre_validate_address_postal_code accepts valid values when in a model"""
        valid_address_postal_codes = ["AA00 00AA", "A0 0AA"]
        valid_json_data = deepcopy(self.patient_json_data)
        for valid_address_postal_code in valid_address_postal_codes:
            valid_json_data["address"][0]["postalCode"] = valid_address_postal_code
            self.assertTrue(self.patient_validator.validate(valid_json_data))

    def test_model_pre_validate_invalid_address_postal_code(self):
        """Test pre_validate_address_postal_code rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.patient_json_data)

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            invalid_json_data["address"][0]["postalCode"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "address -> postalCode must be a string (type=type_error)"
                in str(error.exception)
            )

        # Test empty string
        invalid_json_data["address"][0]["postalCode"] = ""
        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.patient_validator.validate(invalid_json_data)

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
                self.patient_validator.validate(invalid_json_data)

            self.assertTrue(
                "address -> postalCode must contain a single space, which divides the two parts of the postal code (type=value_error)"
                in str(error.exception)
            )

        # Test invalid address_postal_code length
        invalid_json_data["address"][0]["postalCode"] = "AA000 00AA"

        # Check that we get the correct error message and that it contains type=value_error
        with self.assertRaises(ValidationError) as error:
            self.patient_validator.validate(invalid_json_data)

        self.assertTrue(
            "address -> postalCode must be 8 or fewer characters (excluding spaces) (type=value_error)"
            in str(error.exception)
        )
