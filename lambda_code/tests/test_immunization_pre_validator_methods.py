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

    @classmethod
    def setUpClass(cls):
        # set up invalid data types for strings
        cls.invalid_data_types_for_strings = InvalidDataTypes.for_strings
        cls.invalid_data_types_for_lists = InvalidDataTypes.for_lists

    def test_patient_identifier_value_valid(self):
        """Test patient_identifier_value"""
        GenericValidatorMethodTests.string_valid(
            self, ImmunizationPreValidators.patient_identifier_value, ["1234567890"]
        )

    def test_patient_identifier_value_invalid(self):
        """Test patient_identifier_value"""

        GenericValidatorMethodTests.string_invalid(
            self,
            validator=ImmunizationPreValidators.patient_identifier_value,
            field_location="patient -> identifier -> value",
            predefined_string_length=10,
            invalid_length_strings_to_test=["123456789", "12345678901", ""],
        )

    def test_pre_occurrence_date_time_valid(self):
        """Test ImmunizationPreValidators.occurrence_date_time"""

        # Test valid data
        valid_occurrence_date_times = [
            "2000-01-01T00:00:00",
            "2000-01-01T22:22:22",
            "1933-12-31T11:11:11+12:45",
        ]
        for valid_occurrence_date_time in valid_occurrence_date_times:
            self.assertEqual(
                ImmunizationPreValidators.occurrence_date_time(
                    valid_occurrence_date_time
                ),
                valid_occurrence_date_time,
            )

    def test_pre_occurrence_date_time_invalid(self):
        """Test ImmunizationPreValidators.occurrence_date_time"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
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
        GenericValidatorMethodTests.list_valid(
            self,
            validator=ImmunizationPreValidators.contained,
            valid_lists_to_test=[
                [{"resourceType": "QuestionnaireResponse", "status": "completed"}]
            ],
        )

    def test_pre_contained_invalid(self):
        """Test ImmunizationPreValidators.contained"""

        invalid_length_lists_to_test = (
            [
                [],
                [
                    {"resourceType": "QuestionnaireResponse", "status": "completed"},
                    {"resourceType": "QuestionnaireResponse", "status": "completed"},
                ],
            ],
        )

        GenericValidatorMethodTests.list_invalid(
            self,
            validator=ImmunizationPreValidators.contained,
            field_location="contained",
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_length_lists_to_test,
        )

    def test_pre_questionnaire_answer_valid(self):
        """Test ImmunizationPreValidators.questionnaire_answer"""
        GenericValidatorMethodTests.list_valid(
            self,
            validator=ImmunizationPreValidators.questionnaire_answer,
            valid_lists_to_test=[
                [
                    {"valueCoding": {"code": "B0C4P"}},
                ]
            ],
        )

    def test_pre_questionnaire_answer_invalid(self):
        """Test ImmunizationPreValidators.questionnaire_answer"""

        invalid_length_lists_to_test = (
            [
                [],
                [
                    {"valueCoding": {"code": "B0C4P"}},
                    {"valueCoding": {"code": "B0C4P"}},
                ],
            ],
        )

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

        GenericValidatorMethodTests.string_valid(
            self,
            validator=ImmunizationPreValidators.questionnaire_site_code_code,
            valid_strings_to_test=["B0C4P"],
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

        GenericValidatorMethodTests.string_valid(
            self,
            validator=ImmunizationPreValidators.questionnaire_site_name_code,
            valid_strings_to_test=["dummy"],
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

        GenericValidatorMethodTests.list_valid(
            self,
            validator=ImmunizationPreValidators.identifier,
            valid_lists_to_test=valid_lists_to_test,
        )

    def test_pre_identifier_invalid(self):
        """Test ImmunizationPreValidators.identifier"""

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.identifier(invalid_data_type_for_list)

        invalid_length_lists_to_test = [
            [],
            [
                {
                    "system": "https://supplierABC/identifiers/vacc",
                    "value": "e045626e-4dc5-4df3-bc35-da25263f901e",
                },
                {
                    "system": "https://supplierABC/identifiers/vacc",
                    "value": "e045626e-4dc5-4df3-bc35-da25263f901e",
                },
            ],
        ]

        GenericValidatorMethodTests.list_invalid(
            self,
            validator=ImmunizationPreValidators.identifier,
            field_location="identifier",
            predefined_list_length=1,
            invalid_length_lists_to_test=invalid_length_lists_to_test,
        )

    def test_pre_identifier_value_valid(self):
        """Test ImmunizationPreValidators.identifier_value"""

        GenericValidatorMethodTests.string_valid(
            self,
            validator=ImmunizationPreValidators.identifier_value,
            valid_strings_to_test=[
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

        GenericValidatorMethodTests.string_valid(
            self,
            validator=ImmunizationPreValidators.identifier_system,
            valid_strings_to_test=[
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
