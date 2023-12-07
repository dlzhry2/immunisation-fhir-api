"""Test immunization pre-validation methods"""

import unittest

from models.immunization_pre_validators import ImmunizationPreValidators
from ..tests.utils import (
    InvalidDataTypes,
    GenericValidatorMethodTests,
    generate_field_location_for_questionnnaire_response,
)


class TestPreImmunizationMethodValidators(unittest.TestCase):
    """Test immunization pre-validation methods"""

    def test_patient_identifier_value_valid(self):
        """Test patient_identifier_value"""
        GenericValidatorMethodTests.valid(
            self, ImmunizationPreValidators.patient_identifier_value, ["1234567890"]
        )

    def test_patient_identifier_value_invalid(self):
        """Test patient_identifier_value"""

        GenericValidatorMethodTests.string_invalid(
            self,
            validator=ImmunizationPreValidators.patient_identifier_value,
            field_location="patient -> identifier -> value",
            defined_length=10,
            invalid_length_strings_to_test=["123456789", "12345678901"],
        )

    def test_pre_occurrence_date_time_valid(self):
        """Test ImmunizationPreValidators.occurrence_date_time"""

        # Test valid data
        valid_items_to_test = [
            "2000-01-01T00:00:00",
            "2000-01-01T22:22:22",
            "1933-12-31T11:11:11+12:45",
        ]

        GenericValidatorMethodTests.valid(
            self,
            ImmunizationPreValidators.occurrence_date_time,
            valid_items_to_test=valid_items_to_test,
        )

    def test_pre_occurrence_date_time_invalid(self):
        """Test ImmunizationPreValidators.occurrence_date_time"""

        # Test invalid data types
        for invalid_data_type_for_string in InvalidDataTypes.for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.occurrence_date_time(
                    invalid_data_type_for_string
                )

            self.assertEqual(
                str(error.exception),
                "occurrenceDateTime must be a string",
            )

        # Test invalid date string formats
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
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.occurrence_date_time(
                    invalid_occurrence_date_time
                )
            self.assertEqual(
                str(error.exception),
                'occurrenceDateTime must be a string in the format "YYYY-MM-DDThh:mm:ss" '
                + 'or "YYYY-MM-DDThh:mm:ss+zz"',
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
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.occurrence_date_time(
                    invalid_occurrence_date_time
                )
            self.assertEqual(
                str(error.exception),
                "occurrenceDateTime must be a valid datetime",
            )

    def test_pre_contained_valid(self):
        """Test ImmunizationPreValidators.contained"""
        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.contained,
            valid_items_to_test=[
                [{"resourceType": "QuestionnaireResponse", "status": "completed"}]
            ],
        )

    def test_pre_contained_invalid(self):
        """Test ImmunizationPreValidators.contained"""
        valid_list_element = {
            "resourceType": "QuestionnaireResponse",
            "status": "completed",
        }
        invalid_length_lists_to_test = [[valid_list_element, valid_list_element]]

        GenericValidatorMethodTests.list_invalid(
            self,
            validator=ImmunizationPreValidators.contained,
            field_location="contained",
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_length_lists_to_test,
        )

    def test_pre_questionnaire_answer_valid(self):
        """Test ImmunizationPreValidators.questionnaire_answer"""
        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.questionnaire_answer,
            valid_items_to_test=[
                [
                    {"valueCoding": {"code": "B0C4P"}},
                ]
            ],
        )

    def test_pre_questionnaire_answer_invalid(self):
        """Test ImmunizationPreValidators.questionnaire_answer"""
        valid_list_element = {"valueCoding": {"code": "B0C4P"}}
        invalid_length_lists_to_test = [[valid_list_element, valid_list_element]]

        GenericValidatorMethodTests.list_invalid(
            self,
            validator=ImmunizationPreValidators.questionnaire_answer,
            field_location="contained[0] -> resourceType[QuestionnaireResponse]: "
            + "item[*] -> linkId[*]: answer",
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_length_lists_to_test,
        )

    def test_pre_questionnaire_site_code_code_valid(self):
        """Test ImmunizationPreValidators.questionnaire_site_code_code"""

        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.questionnaire_site_code_code,
            valid_items_to_test=["B0C4P"],
        )

    def test_pre_questionnaire_site_code_code_invalid(self):
        """Test ImmunizationPreValidators.questionnaire_site_code_code"""

        GenericValidatorMethodTests.string_invalid(
            self,
            validator=ImmunizationPreValidators.questionnaire_site_code_code,
            field_location=generate_field_location_for_questionnnaire_response(
                "SiteCode", "code"
            ),
        )

    def test_pre_questionnaire_site_name_code_valid(self):
        """Test ImmunizationPreValidators.questionnaire_site_name_code"""

        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.questionnaire_site_name_code,
            valid_items_to_test=["dummy"],
        )

    def test_pre_questionnaire_site_name_code_invalid(self):
        """Test ImmunizationPreValidators.questionnaire_site_name_code"""

        GenericValidatorMethodTests.string_invalid(
            self,
            validator=ImmunizationPreValidators.questionnaire_site_name_code,
            field_location=generate_field_location_for_questionnnaire_response(
                "SiteName", "code"
            ),
        )

    def test_pre_identifier_valid(self):
        """Test ImmunizationPreValidators.identifier"""

        valid_lists_to_test = [
            [
                {
                    "system": "https://supplierABC/identifiers/vacc",
                    "value": "e045626e-4dc5-4df3-bc35-da25263f901e",
                }
            ]
        ]

        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.identifier,
            valid_items_to_test=valid_lists_to_test,
        )

    def test_pre_identifier_invalid(self):
        """Test ImmunizationPreValidators.identifier"""

        valid_list_element = {
            "system": "https://supplierABC/identifiers/vacc",
            "value": "e045626e-4dc5-4df3-bc35-da25263f901e",
        }
        invalid_length_lists_to_test = [[valid_list_element, valid_list_element]]

        GenericValidatorMethodTests.list_invalid(
            self,
            validator=ImmunizationPreValidators.identifier,
            field_location="identifier",
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_length_lists_to_test,
        )

    def test_pre_identifier_value_valid(self):
        """Test ImmunizationPreValidators.identifier_value"""

        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.identifier_value,
            valid_items_to_test=[
                "e045626e-4dc5-4df3-bc35-da25263f901e",
                "ACME-vacc123456",
                "ACME-CUSTOMER1-vacc123456",
            ],
        )

    def test_pre_identifier_value_invalid(self):
        """Test ImmunizationPreValidators.identifier_value"""

        GenericValidatorMethodTests.string_invalid(
            self,
            validator=ImmunizationPreValidators.identifier_value,
            field_location="identifier[0] -> value",
        )

    def test_pre_identifier_system_valid(self):
        """Test ImmunizationPreValidators.identifier_system"""

        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.identifier_system,
            valid_items_to_test=[
                "https://supplierABC/identifiers/vacc",
                "https://supplierABC/ODSCode_NKO41/identifiers/vacc",
            ],
        )

    def test_pre_identifier_system_invalid(self):
        """Test ImmunizationPreValidators.identifier_system"""

        GenericValidatorMethodTests.string_invalid(
            self,
            validator=ImmunizationPreValidators.identifier_system,
            field_location="identifier[0] -> system",
        )

    def test_pre_status_valid(self):
        """Test ImmunizationPreValidators.status"""

        GenericValidatorMethodTests.valid(
            self,
            validator=ImmunizationPreValidators.status,
            valid_items_to_test=["completed", "entered-in-error", "not-done"],
        )

    def test_pre_status_invalid(self):
        """Test ImmunizationPreValidators.status"""
        GenericValidatorMethodTests.string_invalid(
            self,
            validator=ImmunizationPreValidators.status,
            field_location="status",
            predefined_values=("completed", "entered-in-error", "not-done"),
            invalid_strings_to_test=["1", "complete", "enteredinerror"],
        )
