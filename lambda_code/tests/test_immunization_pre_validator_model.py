"""Test immunization pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from pydantic import ValidationError


from models.fhir_immunization import ImmunizationValidator
from lambda_code.tests.utils import (
    InvalidDataTypes,
    GenericValidatorModelTests,
    generate_field_location_for_questionnnaire_response,
)


class TestImmunizationModelPreValidationRules(unittest.TestCase):
    """
    Test immunization pre validation rules on the model

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

        # set up the sample immunization event JSON data
        cls.immunization_file_path = f"{cls.data_path}/sample_immunization_event.json"
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f)

        # set up the untouched sample immunization event JSON data
        cls.untouched_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = ImmunizationValidator()
        cls.validator.add_custom_root_validators()

        # set up invalid data types for strings
        cls.invalid_data_types_for_strings = InvalidDataTypes.for_strings
        # set up invalid data types for lists
        cls.invalid_data_types_for_lists = InvalidDataTypes.for_lists

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_json_data, self.json_data)

    def test_model_pre_validate_valid_patient_identifier_value(self):
        """Test pre_validate_patient_identifier_value accepts valid values when in a model"""

        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["patient", "identifier", "value"],
            valid_items_to_test=["1234567890"],
        )

    def test_model_pre_validate_invalid_patient_identifier_value(self):
        """Test pre_validate_patient_identifier_value rejects invalid values when in a model"""

        GenericValidatorModelTests.string_invalid(
            self,
            field_location="patient -> identifier -> value",
            keys_to_access_value=["patient", "identifier", "value"],
            defined_length=10,
            invalid_length_strings_to_test=["123456789", "12345678901", ""],
        )

    def test_model_pre_validate_valid_occurrence_date_time(self):
        """Test pre_validate_occurrence_date_time accepts valid values when in a model"""
        valid_items_to_test = [
            "2000-01-01T00:00:00",
            "2000-01-01T22:22:22",
            "1933-12-31T11:11:11+12:45",
            "1933-12-31T11:11:11-05:00",
        ]

        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["occurrenceDateTime"],
            valid_items_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_occurrence_date_time(self):
        """Test pre_validate_occurrence_date_time rejects invalid values when in a model"""

        invalid_json_data = deepcopy(self.json_data)

        # Test none (this should be rejected by the model prior to the pre-validate function
        # running as FHIR cardinality is 1..1)
        invalid_json_data["occurrenceDateTime"] = None
        # Check that we get the correct error message and that it contains type=type_error
        with self.assertRaises(ValidationError) as error:
            self.validator.validate(invalid_json_data)

        self.assertTrue(
            "Expect any of field value from this list "
            + "['occurrenceDateTime', 'occurrenceString']. (type=value_error)"
            in str(error.exception)
        )

        # Test invalid data types (other than none)
        for invalid_data_type_for_string in filter(
            None, self.invalid_data_types_for_strings
        ):
            invalid_json_data["occurrenceDateTime"] = invalid_data_type_for_string
            # Check that we get the correct error message and that it contains type=type_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "occurrenceDateTime must be a string (type=type_error)"
                in str(error.exception)
            )

        invalid_occurrence_date_times = [
            "",
            "invalid",
            "20000101",
            "20000101000000",
            "200001010000000000",
            "2000-01-01",
            "2000-01-01T00:00:001",
            "12000-01-01T00:00:00+00:00",
            "12000-01-02T00:00:001",
            "12000-01-02T00:00:00+00:001",
            "2000-01-0122:22:22",
            "2000-01-0122:22:22+00:00",
            "2000-01-01T22:22:2200:00",
            "2000-01-01T22:22:22+0000",
            "99-01-01T00:00:00",
            "01-01-99T00:00:00",
            "01-01-1999T00:00:00",
        ]

        for invalid_occurrence_date_time in invalid_occurrence_date_times:
            invalid_json_data["occurrenceDateTime"] = invalid_occurrence_date_time

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                'occurrenceDateTime must be a string in the format "YYYY-MM-DDThh:mm:ss" '
                + 'or "YYYY-MM-DDThh:mm:ss+zz:zz" or "YYYY-MM-DDThh:mm:ss-zz:zz" (type=value_error)'
                in str(error.exception)
            )

        # Test invalid dates
        invalid_occurrence_date_times = [
            "2000-00-01T00:00:00",
            "2000-13-01T00:00:00",
            "2000-01-00T00:00:00",
            "2000-01-32T00:00:00",
            "2000-02-30T00:00:00",
            "2000-01-01T24:00:00",
            "2000-01-01T00:60:00",
            "2000-01-01T00:00:60",
            "2000-01-01T00:00:00+24:00",
            "2000-01-01T00:00:00+00:60",
        ]

        for invalid_occurrence_date_time in invalid_occurrence_date_times:
            invalid_json_data["occurrenceDateTime"] = invalid_occurrence_date_time

            # Check that we get the correct error message and that it contains type=value_error
            with self.assertRaises(ValidationError) as error:
                self.validator.validate(invalid_json_data)

            self.assertTrue(
                "occurrenceDateTime must be a valid datetime (type=value_error)"
                in str(error.exception)
            )

    def test_model_pre_validate_valid_contained(self):
        """Test pre_validate_contained accepts valid values when in a model"""
        valid_items_to_test = [
            [{"resourceType": "QuestionnaireResponse", "status": "completed"}]
        ]
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["contained"],
            valid_items_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_contained(self):
        """Test pre_validate_contained rejects invalid values when in a model"""
        valid_list_element = {
            "resourceType": "QuestionnaireResponse",
            "status": "completed",
        }
        invalid_length_lists_to_test = [[valid_list_element, valid_list_element]]

        GenericValidatorModelTests.list_invalid(
            self,
            field_location="contained",
            keys_to_access_value=["contained"],
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_length_lists_to_test,
        )

    def test_model_pre_validate_valid_questionnaire_answers(self):
        """Test pre_validate_questionnaire_answers accepts valid values when in a model"""
        valid_items_to_test = [[{"valueCoding": {"code": "B0C4P"}}]]

        # Check that all of the 12 answer fields in the sample data are accepted when valid
        for i in range(12):
            GenericValidatorModelTests.valid(
                self,
                keys_to_access_value=["contained", 0, "item", i, "answer"],
                valid_items_to_test=valid_items_to_test,
            )

    def test_model_pre_validate_invalid_questionnaire_answers(self):
        """Test pre_validate_quesionnaire_answers rejects invalid values when in a model"""

        valid_list_element = {"valueCoding": {"code": "B0C4P"}}
        invalid_length_lists_to_test = [[valid_list_element, valid_list_element]]

        # Check that any of the 12 answer fields in the sample data are rejected when invalid
        for i in range(12):
            GenericValidatorModelTests.list_invalid(
                self,
                field_location="contained[0] -> resourceType[QuestionnaireResponse]: "
                + "item[*] -> linkId[*]: answer",
                keys_to_access_value=["contained", 0, "item", i, "answer"],
                predefined_list_length=1,
                invalid_length_lists_to_test=invalid_length_lists_to_test,
            )

    def test_model_pre_validate_valid_questionnaire_site_code_code(self):
        """Test pre_validate_questionnaire_site_code_code accepts valid values when in a model"""
        keys_to_access_value = [
            "contained",
            0,
            "item",
            0,
            "answer",
            0,
            "valueCoding",
            "code",
        ]

        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=keys_to_access_value,
            valid_items_to_test=["B0C4P"],
        )

    def test_model_pre_validate_invalid_questionnaire_site_code_code(self):
        """Test pre_validate_questionnaire_site_code_code rejects invalid values when in a model"""

        field_location = generate_field_location_for_questionnnaire_response(
            link_id="SiteCode", field_type="code"
        )

        keys_to_access_value = [
            "contained",
            0,
            "item",
            0,
            "answer",
            0,
            "valueCoding",
            "code",
        ]
        GenericValidatorModelTests.string_invalid(
            self,
            field_location=field_location,
            keys_to_access_value=keys_to_access_value,
        )

    def test_model_pre_validate_valid_questionnaire_site_name_code(self):
        """Test pre_validate_questionnaire_site_name_code accepts valid values when in a model"""

        keys_to_access_value = [
            "contained",
            0,
            "item",
            1,
            "answer",
            0,
            "valueCoding",
            "code",
        ]

        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=keys_to_access_value,
            valid_items_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_questionnaire_site_name_code(self):
        """Test pre_validate_questionnaire_site_code_code rejects invalid values when in a model"""

        field_location = generate_field_location_for_questionnnaire_response(
            link_id="SiteName", field_type="code"
        )

        keys_to_access_value = [
            "contained",
            0,
            "item",
            1,
            "answer",
            0,
            "valueCoding",
            "code",
        ]
        GenericValidatorModelTests.string_invalid(
            self,
            field_location=field_location,
            keys_to_access_value=keys_to_access_value,
        )

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

        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["identifier"],
            valid_items_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_identifier(self):
        """Test pre_validate_identifier rejects invalid values when in a model"""

        valid_list_element = {
            "system": "https://supplierABC/identifiers/vacc",
            "value": "ACME-vacc123456",
        }
        invalid_length_lists_to_test = [[valid_list_element, valid_list_element]]
        GenericValidatorModelTests.list_invalid(
            self,
            field_location="identifier",
            keys_to_access_value=["identifier"],
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_length_lists_to_test,
        )

    def test_model_pre_validate_valid_identifier_value(self):
        """Test pre_validate_identifier_value accepts valid values when in a model"""
        valid_items_to_test = [
            "e045626e-4dc5-4df3-bc35-da25263f901e",
            "ACME-vacc123456",
            "ACME-CUSTOMER1-vacc123456",
        ]

        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["identifier", 0, "value"],
            valid_items_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_identifier_value(self):
        """Test pre_validate_identifier_value rejects invalid values when in a model"""

        GenericValidatorModelTests.string_invalid(
            self,
            field_location="identifier[0] -> value",
            keys_to_access_value=["identifier", 0, "value"],
        )

    def test_model_pre_validate_valid_identifier_system(self):
        """Test pre_validate_identifier_system accepts valid values when in a model"""
        valid_items_to_test = [
            "https://supplierABC/identifiers/vacc",
            "https://supplierABC/ODSCode_NKO41/identifiers/vacc",
        ]

        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["identifier", 0, "system"],
            valid_items_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_identifier_system(self):
        """Test pre_validate_identifier_system rejects invalid values when in a model"""
        GenericValidatorModelTests.string_invalid(
            self,
            field_location="identifier[0] -> system",
            keys_to_access_value=["identifier", 0, "system"],
        )

    def test_model_pre_validate_valid_status(self):
        """Test pre_validate_status accepts valid values when in a model"""
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["status"],
            valid_items_to_test=["completed", "entered-in-error", "not-done"],
        )

    def test_model_pre_validate_invalid_status(self):
        """Test pre_validate_status rejects invalid values when in a model"""
        GenericValidatorModelTests.string_invalid(
            self,
            field_location="status",
            keys_to_access_value=["status"],
            predefined_values=("completed", "entered-in-error", "not-done"),
            invalid_strings_to_test=["1", "complete", "enteredinerror"],
            is_mandatory_fhir=True,
        )

    def test_model_pre_validate_valid_recorded(self):
        """Test pre_validate_recorded accepts valid values when in a model"""
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["recorded"],
            valid_items_to_test=["2000-01-01", "1933-12-31"],
        )

    def test_model_pre_validate_invalid_recorded(self):
        """Test pre_validate_recorded rejects invalid values when in a model"""
        GenericValidatorModelTests.date_invalid(
            self, field_location="recorded", keys_to_access_value=["recorded"]
        )

    def test_model_pre_validate_valid_primary_source(self):
        """Test pre_validate_primary_source accepts valid values when in a model"""
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["primarySource"],
            valid_items_to_test=[True, False],
        )

    def test_model_pre_validate_invalid_primary_source(self):
        """Test pre_validate_primary_source rejects invalid values when in a model"""
        GenericValidatorModelTests.boolean_invalid(
            self, field_location="primarySource", keys_to_access_value=["primarySource"]
        )

    def test_model_pre_validate_valid_report_origin_text(self):
        """Test pre_validate_report_origin_text accepts valid values when in a model"""
        GenericValidatorModelTests.valid(
            self,
            keys_to_access_value=["reportOrigin", "text"],
            valid_items_to_test=[
                "sample",
                "Free text description of organisation recording the event",
            ],
        )

    def test_model_pre_validate_invalid_report_origin_text(self):
        """Test pre_validate_report_origin_text rejects invalid values when in a model"""
        invalid_length_strings_to_test = [
            "This is a really long string with more than 100 "
            + "characters to test whether the validator is working well"
        ]

        GenericValidatorModelTests.string_invalid(
            self,
            field_location="reportOrigin -> text",
            keys_to_access_value=["reportOrigin", "text"],
            max_length=100,
            invalid_length_strings_to_test=invalid_length_strings_to_test,
        )
