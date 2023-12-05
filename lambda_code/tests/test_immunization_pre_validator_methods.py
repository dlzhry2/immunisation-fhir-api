"""Test immunization pre-validation methods"""

import unittest

from models.immunization_pre_validators import ImmunizationPreValidators


class TestPreImmunizationMethodValidators(unittest.TestCase):
    """Test immunization pre-validation methods"""

    @classmethod
    def setUpClass(cls):
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

    def test_patient_identifier_value_valid(self):
        """Test patient_identifier_value"""
        valid_patient_identifier_value = "1234567890"
        self.assertEqual(
            ImmunizationPreValidators.patient_identifier_value(
                valid_patient_identifier_value
            ),
            "1234567890",
        )

    def test_patient_identifier_value_invalid(self):
        """Test patient_identifier_value"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.patient_identifier_value(
                    invalid_data_type_for_string
                )

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> value must be a string",
            )

        # Test invalid string lengths
        invalid_patient_identifier_values = ["123456789", "12345678901", ""]
        for invalid_patient_identifier_value in invalid_patient_identifier_values:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.patient_identifier_value(
                    invalid_patient_identifier_value
                )

            self.assertEqual(
                str(error.exception),
                "patient -> identifier -> value must be 10 characters",
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
        # Test valid data
        valid_contained = [
            {"resourceType": "QuestionnaireResponse", "status": "completed"}
        ]
        self.assertEqual(
            ImmunizationPreValidators.contained(valid_contained),
            valid_contained,
        )

    def test_pre_contained_invalid(self):
        """Test ImmunizationPreValidators.contained"""

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.contained(invalid_data_type_for_list)

            self.assertEqual(
                str(error.exception),
                "contained must be an array",
            )

        # Test invalid list length
        invalid_contained_items = [
            [],
            [
                {"resourceType": "QuestionnaireResponse", "status": "completed"},
                {"resourceType": "QuestionnaireResponse", "status": "completed"},
            ],
        ]
        for invalid_contained in invalid_contained_items:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.contained(invalid_contained)

            self.assertEqual(
                str(error.exception),
                "contained must be an array of length 1",
            )

    def test_pre_questionnaire_answer_valid(self):
        """Test ImmunizationPreValidators.questionnaire_answer"""

        # Test valid data
        valid_questionnaire_answer = [
            {"valueCoding": {"code": "B0C4P"}},
        ]
        self.assertEqual(
            ImmunizationPreValidators.questionnaire_answer(valid_questionnaire_answer),
            valid_questionnaire_answer,
        )

    def test_pre_questionnaire_answer_invalid(self):
        """Test ImmunizationPreValidators.questionnaire_answer"""

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.questionnaire_answer(
                    invalid_data_type_for_list
                )

            self.assertEqual(
                str(error.exception),
                "contained[0] -> resourceType[QuestionnaireResponse]: "
                + "item[*] -> linkId[*]: answer must be an array",
            )

        # Test invalid list length
        invalid_questionnaire_answers = [
            [],
            [
                {"valueCoding": {"code": "B0C4P"}},
                {"valueCoding": {"code": "B0C4P"}},
            ],
        ]
        for invalid_questionnaire_answer in invalid_questionnaire_answers:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.questionnaire_answer(
                    invalid_questionnaire_answer
                )

            self.assertEqual(
                str(error.exception),
                "contained[0] -> resourceType[QuestionnaireResponse]: "
                + "item[*] -> linkId[*]: answer must be an array of length 1",
            )

    def test_pre_questionnaire_site_code_code_valid(self):
        """Test ImmunizationPreValidators.questionnaire_site_code_code"""

        # Test valid data
        valid_questionnaire_site_code_code = "B0C4P"
        self.assertEqual(
            ImmunizationPreValidators.questionnaire_site_code_code(
                valid_questionnaire_site_code_code
            ),
            valid_questionnaire_site_code_code,
        )

    def test_pre_questionnaire_site_code_code_invalid(self):
        """Test ImmunizationPreValidators.questionnaire_site_code_code"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.questionnaire_site_code_code(
                    invalid_data_type_for_string
                )

            self.assertEqual(
                str(error.exception),
                "contained[0] -> resourceType[QuestionnaireResponse]: "
                + "item[*] -> linkId[SiteCode]: answer[0] -> valueCoding -> code must be a string",
            )

        # Test invalid string (empty) in list
        with self.assertRaises(ValueError) as error:
            ImmunizationPreValidators.questionnaire_site_code_code("")
        self.assertEqual(
            str(error.exception),
            "contained[0] -> resourceType[QuestionnaireResponse]: "
            + "item[*] -> linkId[SiteCode]: "
            + "answer[0] -> valueCoding -> code must be a non-empty string",
        )

    def test_pre_questionnaire_site_name_code_valid(self):
        """Test ImmunizationPreValidators.questionnaire_site_name_code"""

        # Test valid data
        valid_questionnaire_site_name_code = "dummy"
        self.assertEqual(
            ImmunizationPreValidators.questionnaire_site_name_code(
                valid_questionnaire_site_name_code
            ),
            valid_questionnaire_site_name_code,
        )

    def test_pre_questionnaire_site_name_code_invalid(self):
        """Test ImmunizationPreValidators.questionnaire_site_name_code"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.questionnaire_site_name_code(
                    invalid_data_type_for_string
                )

            self.assertEqual(
                str(error.exception),
                "contained[0] -> resourceType[QuestionnaireResponse]: "
                + "item[*] -> linkId[SiteName]: answer[0] -> valueCoding -> code must be a string",
            )

        # Test invalid string (empty) in list
        with self.assertRaises(ValueError) as error:
            ImmunizationPreValidators.questionnaire_site_name_code("")
        self.assertEqual(
            str(error.exception),
            "contained[0] -> resourceType[QuestionnaireResponse]: "
            + "item[*] -> linkId[SiteName]: "
            + "answer[0] -> valueCoding -> code must be a non-empty string",
        )

    def test_pre_identifier_valid(self):
        """Test ImmunizationPreValidators.identifier"""

        # Test valid data
        valid_identifier = [
            {
                "system": "https://supplierABC/identifiers/vacc",
                "value": "e045626e-4dc5-4df3-bc35-da25263f901e",
            }
        ]
        self.assertEqual(
            ImmunizationPreValidators.identifier(valid_identifier),
            valid_identifier,
        )

    def test_pre_identifier_invalid(self):
        """Test ImmunizationPreValidators.identifier"""

        # Test invalid data types
        for invalid_data_type_for_list in self.invalid_data_types_for_lists:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.identifier(invalid_data_type_for_list)

            self.assertEqual(
                str(error.exception),
                "identifier must be an array",
            )

        # Test invalid list length
        invalid_identifiers = [
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
        for invalid_identifier in invalid_identifiers:
            with self.assertRaises(ValueError) as error:
                ImmunizationPreValidators.identifier(invalid_identifier)

            self.assertEqual(
                str(error.exception),
                "identifier must be an array of length 1",
            )

    def test_pre_identifier_system_valid(self):
        """Test ImmunizationPreValidators.identifier_system"""

        # Test valid data
        valid_identifier_systems = [
            "https://supplierABC/identifiers/vacc",
            "https://supplierABC/ODSCode_NKO41/identifiers/vacc",
        ]
        for valid_identifier_system in valid_identifier_systems:
            self.assertEqual(
                ImmunizationPreValidators.identifier_value(valid_identifier_system),
                valid_identifier_system,
            )

    def test_pre_identifier_system_invalid(self):
        """Test ImmunizationPreValidators.identifier_system"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.identifier_value(invalid_data_type_for_string)

            self.assertEqual(
                str(error.exception),
                "identifier[0] -> system must be a string",
            )

        # Test invalid string (empty) in list
        with self.assertRaises(ValueError) as error:
            ImmunizationPreValidators.identifier_value("")
        self.assertEqual(
            str(error.exception),
            "identifier[0] -> system must be a non-empty string",
        )

    def test_pre_identifier_value_valid(self):
        """Test ImmunizationPreValidators.identifier_value"""

        # Test valid data
        valid_identifier_values = [
            "e045626e-4dc5-4df3-bc35-da25263f901e",
            "ACME-vacc123456",
            "ACME-CUSTOMER1-vacc123456",
        ]
        for valid_identifier_value in valid_identifier_values:
            self.assertEqual(
                ImmunizationPreValidators.identifier_value(valid_identifier_value),
                valid_identifier_value,
            )

    def test_pre_identifier_value_invalid(self):
        """Test ImmunizationPreValidators.identifier_value"""

        # Test invalid data types
        for invalid_data_type_for_string in self.invalid_data_types_for_strings:
            with self.assertRaises(TypeError) as error:
                ImmunizationPreValidators.identifier_value(invalid_data_type_for_string)

            self.assertEqual(
                str(error.exception),
                "identifier[0] -> value must be a string",
            )

        # Test invalid string (empty) in list
        with self.assertRaises(ValueError) as error:
            ImmunizationPreValidators.identifier_value("")
        self.assertEqual(
            str(error.exception),
            "identifier[0] -> value must be a non-empty string",
        )
