"""Test immunization pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from decimal import Decimal
from models.fhir_immunization import ImmunizationValidator
from jsonpath_ng.ext import parse
from pydantic import ValidationError
from .utils.generic_utils import (
    generate_field_location_for_questionnnaire_response,
    generate_field_location_for_extension,
    test_valid_values_accepted as _test_valid_values_accepted,
    test_invalid_values_rejected as _test_invalid_values_rejected,
)
from .utils.pre_validation_test_utils import (
    ValidatorModelTests,
)
from .utils.values_for_tests import ValidValues, InvalidValues


class TestImmunizationModelPreValidationRules(unittest.TestCase):
    """Test immunization pre validation rules on the FHIR model"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample immunization event JSON data
        cls.immunization_file_path = (
            f"{cls.data_path}/sample_covid_immunization_event.json"
        )
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f, parse_float=Decimal)

        # set up the untouched sample immunization event JSON data
        cls.untouched_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = ImmunizationValidator()
        cls.validator.add_custom_root_pre_validators()

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_json_data, self.json_data)

    def test_model_pre_validate_contained(self):
        """Test pre_validate_contained accepts valid values and rejects invalid values"""
        # Test that the contained field is rejected when invalid
        valid_lists_to_test = [
            [
                {
                    "resourceType": "Practitioner",
                    "id": "Pract1",
                },
                {
                    "resourceType": "Patient",
                    "id": "Pat1",
                },
                {
                    "resourceType": "QuestionnaireResponse",
                    "id": "QR1",
                    "status": "completed",
                },
            ]
        ]
        invalid_list_to_test = [
            {
                "resourceType": "Practitioner",
                "id": "Pract1",
            },
            {
                "resourceType": "Patient",
                "id": "Pat1",
            },
            {
                "resourceType": "Patient",
                "id": "Pat2",
            },
            {
                "resourceType": "QuestionnaireResponse",
                "id": "QR1",
                "status": "completed",
            },
        ]

        ValidatorModelTests.test_unique_list(
            self,
            field_location="contained",
            valid_lists_to_test=valid_lists_to_test,
            invalid_list_with_duplicates_to_test=invalid_list_to_test,
            expected_error_message="contained[?(@.resourceType=='Patient')] must be unique",
        )

    def test_model_pre_validate_patient_identifier(self):
        """Test pre_validate_patient_identifier accepts valid values and rejects invalid values"""
        valid_list_element = {
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": "9000000009",
        }

        ValidatorModelTests.test_list_value(
            self,
            field_location="contained[?(@.resourceType=='Patient')].identifier",
            valid_lists_to_test=[[valid_list_element]],
            predefined_list_length=1,
            valid_list_element=valid_list_element,
        )

    def test_model_pre_validate_patient_identifier_value(self):
        """
        Test pre_validate_patient_identifier_value accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='Patient')].identifier[0].value",
            valid_strings_to_test=["1234567890"],
            defined_length=10,
            invalid_length_strings_to_test=["123456789", "12345678901", ""],
            spaces_allowed=False,
            invalid_strings_with_spaces_to_test=[
                "12345 7890",
                " 123456789",
                "123456789 ",
                "1234  7890",
            ],
        )

    def test_model_pre_validate_patient_name(self):
        """Test pre_validate_patient_name accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_list_value(
            self,
            field_location="contained[?(@.resourceType=='Patient')].name",
            valid_lists_to_test=[[{"family": "Test"}]],
            predefined_list_length=1,
            valid_list_element={"family": "Test"},
        )

    def test_model_pre_validate_patient_name_given(self):
        """Test pre_validate_patient_name_given accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_list_value(
            self,
            field_location="contained[?(@.resourceType=='Patient')].name[0].given",
            valid_lists_to_test=[["Test"], ["Test test"]],
            predefined_list_length=1,
            valid_list_element="Test",
            is_list_of_strings=True,
        )

    def test_model_pre_validate_patient_name_family(self):
        """Test pre_validate_patient_name_family accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='Patient')].name[0].family",
            valid_strings_to_test=["test"],
        )

    def test_model_pre_validate_patient_birth_date(self):
        """Test pre_validate_patient_birth_date accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_date_value(
            self, field_location="contained[?(@.resourceType=='Patient')].birthDate"
        )

    def test_model_pre_validate_patient_gender(self):
        """Test pre_validate_patient_gender accepts valid values and rejects invalid values"""
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
            field_location="contained[?(@.resourceType=='Patient')].gender",
            valid_strings_to_test=["male", "female", "other", "unknown"],
            predefined_values=("male", "female", "other", "unknown"),
            invalid_strings_to_test=invalid_strings_to_test,
        )

    def test_model_pre_validate_patient_address(self):
        """Test pre_validate_patient_address accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_list_value(
            self,
            field_location="contained[?(@.resourceType=='Patient')].address",
            valid_lists_to_test=[[{"postalCode": "AA1 1AA"}]],
            predefined_list_length=1,
            valid_list_element={"family": "Test"},
        )

    def test_model_pre_validate_patient_address_postal_code(self):
        """
        Test pre_validate_patient_address_postal_code accepts valid values and rejects
        invalid values
        """
        # Test invalid data types and empty string
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='Patient')].address[0].postalCode",
            valid_strings_to_test=["AA00 00AA", "A0 0AA"],
            is_postal_code=True,
        )

    def test_model_pre_validate_occurrence_date_time(self):
        """
        Test pre_validate_occurrence_date_time accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_date_time_value(
            self,
            field_location="occurrenceDateTime",
            is_occurrence_date_time=True,
        )

    def test_model_pre_validate_valid_questionnaire_answers(self):
        """
        Test pre_validate_quesionnaire_answers accepts valid values and rejects invalid values
        """
        # Check that any of the answer fields in the sample data are rejected when invalid
        for i in range(len(self.json_data["contained"][2]["item"])):
            # Determine what valid list element looks like
            answer_keys = self.json_data["contained"][2]["item"][i]["answer"][0].keys()
            if "valueCoding" in answer_keys:
                valid_list_element = {"valueCoding": {"code": "True"}}
            elif "valueBoolean" in answer_keys:
                valid_list_element = {"valueBoolean": True}
            elif "valueString" in answer_keys:
                valid_list_element = {"valueString": "test_string"}
            elif "valueDateTime" in answer_keys:
                valid_list_element = {"valueDateTime": "2021-02-07T13:44:07+00:00"}
            elif "valueReference" in answer_keys:
                valid_list_element = {"valueReference": {"reference": "#"}}

            ValidatorModelTests.test_list_value(
                self,
                field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
                + f".item[{i}].answer",
                valid_lists_to_test=[[valid_list_element]],
                predefined_list_length=1,
                valid_list_element=valid_list_element,
            )

    def test_model_pre_validate_questionnaire_response_item(self):
        """
        Test pre_validate_questionnaire_response_item accepts valid values and rejects invalid
        values
        """
        # Test that the contained field is rejected when invalid
        valid_lists_to_test = [
            [
                {
                    "linkId": "Immunisation",
                    "answer": [{"valueReference": {"reference": "#"}}],
                },
                {"linkId": "ReduceValidation", "answer": [{"valueBoolean": False}]},
                {
                    "linkId": "IpAddress",
                    "answer": [
                        {"valueString": "IP_ADDRESS"},
                    ],
                },
            ]
        ]
        invalid_list_to_test = [
            {
                "linkId": "Immunisation",
                "answer": [{"valueReference": {"reference": "#"}}],
            },
            {"linkId": "ReduceValidation", "answer": [{"valueBoolean": False}]},
            {"linkId": "ReduceValidation", "answer": [{"valueBoolean": True}]},
            {
                "linkId": "IpAddress",
                "answer": [
                    {"valueString": "IP_ADDRESS"},
                ],
            },
        ]

        ValidatorModelTests.test_unique_list(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')].item",
            valid_lists_to_test=valid_lists_to_test,
            invalid_list_with_duplicates_to_test=invalid_list_to_test,
            expected_error_message="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='ReduceValidation')] must be unique",
        )

    def test_model_pre_validate_performer_actor_type(self):
        """
        Test pre_validate_performer_actor_type accepts valid values and rejects invalid
        values
        """

        valid_json_data = deepcopy(self.json_data)

        valid_performers_to_test = [
            [
                {"actor": {"reference": "#Pract1"}},
                {
                    "actor": {
                        "type": "Organization",
                        "display": "Acme Healthcare",
                    }
                },
            ]
        ]

        invalid_performer = [
            {"actor": {"reference": "#Pract1", "type": "Organization"}},
            {
                "actor": {
                    "type": "Organization",
                    "display": "Acme Healthcare",
                }
            },
        ]

        # Test that valid data is accepted
        _test_valid_values_accepted(
            self, valid_json_data, "performer", valid_performers_to_test
        )

        # Test lists with duplicate values
        _test_invalid_values_rejected(
            self,
            valid_json_data,
            field_location="performer",
            invalid_value=invalid_performer,
            expected_error_message="performer.actor[?@.type=='Organization'] must be unique",
            expected_error_type="value_error",
        )

    def test_model_pre_validate_performer_actor_reference(self):
        """
        Test pre_validate_performer_actor_type accepts valid values and rejects invalid
        values
        """

        valid_json_data = deepcopy(self.json_data)
        invalid_json_data = deepcopy(self.json_data)

        valid_contained_with_no_practitioner = [
            {
                "resourceType": "Patient",
                "id": "Pat1",
            },
        ]

        valid_contained_with_practitioner = [
            {
                "resourceType": "Practitioner",
                "id": "Pract1",
            },
            {
                "resourceType": "Patient",
                "id": "Pat1",
            },
        ]

        valid_performer_with_no_contained_practitioner_reference = [
            {"actor": {"reference": "#Pract0"}},
            {
                "actor": {
                    "type": "Organization",
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "B0C4P",
                    },
                    "display": "Acme Healthcare",
                }
            },
        ]

        valid_performer_with_one_contained_practitioner_reference = [
            {"actor": {"reference": "#Pract0"}},
            {"actor": {"reference": "#Pract1"}},
            {
                "actor": {
                    "type": "Organization",
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "B0C4P",
                    },
                    "display": "Acme Healthcare",
                }
            },
        ]

        valid_performer_with_more_than_one_contained_practitioner_reference = [
            {"actor": {"reference": "#Pract1"}},
            {"actor": {"reference": "#Pract1"}},
            {
                "actor": {
                    "type": "Organization",
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "B0C4P",
                    },
                    "display": "Acme Healthcare",
                }
            },
        ]

        # Test case: Pract1 in contained, 0 actor of #Pract1 in performer - reject
        invalid_json_data = parse("contained").update(
            invalid_json_data, valid_contained_with_practitioner
        )
        invalid_json_data = parse("performer").update(
            invalid_json_data, valid_performer_with_no_contained_practitioner_reference
        )
        with self.assertRaises(ValidationError) as error:
            self.validator.validate(invalid_json_data)

        self.assertTrue(
            (
                "Pract1 must be referenced by exactly ONE performer.actor"
                + " (type=value_error)"
            )
            in str(error.exception)
        )

        # Test case: Pract1 in contained, 1 actor of Pract1 in performer - accept
        valid_json_data = parse("contained").update(
            valid_json_data, valid_contained_with_practitioner
        )
        valid_json_data = parse("performer").update(
            valid_json_data, valid_performer_with_one_contained_practitioner_reference
        )

        self.assertTrue(self.validator.validate(valid_json_data))

        # Test Case: Pract1 in contained, 2 actors of Pract1 in performer - reject
        invalid_json_data = parse("contained").update(
            invalid_json_data, valid_contained_with_practitioner
        )
        invalid_json_data = parse("performer").update(
            invalid_json_data,
            valid_performer_with_more_than_one_contained_practitioner_reference,
        )
        with self.assertRaises(ValidationError) as error:
            self.validator.validate(invalid_json_data)

        self.assertTrue(
            (
                "Pract1 must be referenced by exactly ONE performer.actor"
                + " (type=value_error)"
            )
            in str(error.exception)
        )

        # Test case: No practitioner in contained, 0 actor with reference in performer - accept
        valid_json_data = parse("contained").update(
            valid_json_data, valid_contained_with_no_practitioner
        )
        valid_json_data = parse("performer").update(
            valid_json_data, valid_performer_with_no_contained_practitioner_reference
        )

        self.assertTrue(self.validator.validate(valid_json_data))

        # Test case: No practitioner in contained, 1 or more actors with reference in performer
        # - accept
        valid_json_data = parse("contained").update(
            valid_json_data, valid_contained_with_no_practitioner
        )
        valid_json_data = parse("performer").update(
            valid_json_data, valid_performer_with_one_contained_practitioner_reference
        )

        self.assertTrue(self.validator.validate(valid_json_data))

        valid_json_data = parse("performer").update(
            valid_json_data,
            valid_performer_with_more_than_one_contained_practitioner_reference,
        )

        self.assertTrue(self.validator.validate(valid_json_data))

    def test_model_pre_validate_organization_identifier_value(self):
        """
        Test pre_validate_organization_identifier_value accepts valid values and rejects invalid
        values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="performer[?(@.actor.type=='Organization')].actor.identifier.value",
            valid_strings_to_test=["B0C4P"],
        )

    def test_model_pre_validate_organization_display(self):
        """Test pre_validate_organization_display accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="performer[?@.actor.type == 'Organization'].actor.display",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_identifier(self):
        """Test pre_validate_identifier accepts valid values and rejects invalid values"""
        valid_list_element = {
            "system": "https://supplierABC/identifiers/vacc",
            "value": "ACME-vacc123456",
        }

        ValidatorModelTests.test_list_value(
            self,
            field_location="identifier",
            valid_lists_to_test=[[valid_list_element]],
            predefined_list_length=1,
            valid_list_element=valid_list_element,
        )

    def test_model_pre_validate_identifier_value(self):
        """Test pre_validate_identifier_value accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="identifier[0].value",
            valid_strings_to_test=[
                "e045626e-4dc5-4df3-bc35-da25263f901e",
                "ACME-vacc123456",
                "ACME-CUSTOMER1-vacc123456",
            ],
        )

    def test_model_pre_validate_identifier_system(self):
        """Test pre_validate_identifier_system accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="identifier[0].system",
            valid_strings_to_test=[
                "https://supplierABC/identifiers/vacc",
                "https://supplierABC/ODSCode_NKO41/identifiers/vacc",
            ],
        )

    def test_model_pre_validate_status(self):
        """Test pre_validate_status accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="status",
            valid_strings_to_test=["completed", "entered-in-error", "not-done"],
            predefined_values=("completed", "entered-in-error", "not-done"),
            invalid_strings_to_test=["1", "complete", "enteredinerror"],
            is_mandatory_fhir=True,
        )

    def test_model_pre_validate_recorded(self):
        """Test pre_validate_recorded accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_date_value(self, field_location="recorded")

    def test_model_pre_validate_primary_source(self):
        """Test pre_validate_primary_source accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_boolean_value(self, field_location="primarySource")

    def test_model_pre_validate_report_origin_text(self):
        """Test pre_validate_report_origin_text accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="reportOrigin.text",
            valid_strings_to_test=[
                "sample",
                "Free text description of organisation recording the event",
            ],
            max_length=100,
            invalid_length_strings_to_test=InvalidValues.for_strings_with_max_100_chars,
        )

    def test_model_pre_validate_extension_urls(self):
        """
        Test pre_validate_extension_urls accepts valid values and rejects invalid
        values
        """
        valid_extension_item = {
            "url": "https://fhir.hl7.org.uk/StructureDefinition"
            + "/Extension-UKCore-VaccinationProcedure",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "1324681000000101",
                        "display": "Administration of first dose of severe acute "
                        + "respiratory syndrome coronavirus 2 vaccine (procedure)",
                    }
                ]
            },
        }

        ValidatorModelTests.test_unique_list(
            self,
            field_location="extension",
            valid_lists_to_test=[[valid_extension_item]],
            invalid_list_with_duplicates_to_test=[
                valid_extension_item,
                valid_extension_item,
            ],
            expected_error_message="extension[?(@.url=='https://fhir.hl7.org.uk"
            + "/StructureDefinition/Extension-UKCore-VaccinationProcedure')] must be unique",
        )

    def test_model_pre_validate_extension_value_codeable_concept_codings(self):
        """
        Test pre_validate_extension_value_codeable_concept_codings accepts valid values and rejects
        invalid values
        """

        valid_extension_values = [
            [
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition"
                    + "/Extension-UKCore-VaccinationProcedure",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "1324681000000101",
                                "display": "Administration of first dose of severe acute "
                                + "respiratory syndrome coronavirus 2 vaccine (procedure)",
                            },
                            {
                                "system": "dm+d url",
                                "code": "DUMMY DM+D CODE",
                                "display": "Administration of first dose of severe acute "
                                + "respiratory syndrome coronavirus 2 vaccine (procedure)",
                            },
                        ]
                    },
                },
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition"
                    + "/Extension-UKCore-VaccinationSituation",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "SOME DUMMY SNOMED CODE",
                                "display": "DUMMY TERM FOR THE SNOMED CODE",
                            }
                        ]
                    },
                },
            ]
        ]

        invalid_extension_value = [
            {
                "url": "https://fhir.hl7.org.uk/StructureDefinition"
                + "/Extension-UKCore-VaccinationProcedure",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "1324681000000101",
                            "display": "Administration of first dose of severe acute "
                            + "respiratory syndrome coronavirus 2 vaccine (procedure)",
                        }
                    ]
                },
            },
            {
                "url": "https://fhir.hl7.org.uk/StructureDefinition"
                + "/Extension-UKCore-VaccinationSituation",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "SOME DUMMY SNOMED CODE",
                            "display": "DUMMY TERM FOR THE SNOMED CODE",
                        },
                        {
                            "system": "http://snomed.info/sct",
                            "code": "A DIFFERENT SNOMED CODE",
                            "display": "DUMMY TERM FOR THE SNOMED CODE",
                        },
                    ]
                },
            },
        ]

        ValidatorModelTests.test_unique_list(
            self,
            field_location="extension",
            valid_lists_to_test=valid_extension_values,
            invalid_list_with_duplicates_to_test=invalid_extension_value,
            expected_error_message="extension[?(@.URL=='https://fhir.hl7.org.uk"
            + "/StructureDefinition/Extension-UKCore-VaccinationSituation']"
            + ".valueCodeableConcept.coding[?(@.system=='http://snomed.info/sct')] must be unique",
        )

    def test_model_pre_validate_vaccination_procedure_code(self):
        """
        Test pre_validate_vaccination_procedure_code accepts valid values and rejects invalid
        values
        """

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
            system="http://snomed.info/sct",
            field_type="code",
        )

        ValidatorModelTests.test_string_value(
            self, field_location=field_location, valid_strings_to_test=["dummy"]
        )

    def test_model_pre_validate_vaccination_procedure_display(self):
        """
        Test pre_validate_vaccination_procedure_display accepts valid values and rejects
        invalid values
        """

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
            system="http://snomed.info/sct",
            field_type="display",
        )

        ValidatorModelTests.test_string_value(
            self, field_location=field_location, valid_strings_to_test=["dummy"]
        )

    def test_model_pre_validate_protocol_applied(self):
        """Test pre_validate_protocol_applied accepts valid values and rejects invalid values"""
        valid_list_element = {
            "targetDisease": [
                {"coding": [{"code": "ABC123"}]},
                {"coding": [{"code": "DEF456"}]},
            ],
            "doseNumberPositiveInt": 1,
        }

        ValidatorModelTests.test_list_value(
            self,
            field_location="protocolApplied",
            valid_lists_to_test=[[valid_list_element]],
            predefined_list_length=1,
            valid_list_element=valid_list_element,
        )

    def test_model_pre_validate_protocol_applied_dose_number_positive_int(self):
        """
        Test pre_validate_protocol_applied_dose_number_positive_int accepts valid values and
        rejects invalid values
        """
        # Test invalid data types and non-positive integers
        ValidatorModelTests.test_positive_integer_value(
            self,
            field_location="protocolApplied[0].doseNumberPositiveInt",
            valid_positive_integers_to_test=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            max_value=9,
        )

    def test_model_pre_validate_vaccine_code_coding(self):
        """Test pre_validate_vaccine_code_coding accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_unique_list(
            self,
            field_location="vaccineCode.coding",
            valid_lists_to_test=[[ValidValues.snomed_coding_element]],
            invalid_list_with_duplicates_to_test=[
                ValidValues.snomed_coding_element,
                ValidValues.snomed_coding_element,
            ],
            expected_error_message="vaccineCode.coding[?(@.system=='http://snomed.info/sct')]"
            + " must be unique",
        )

    def test_model_pre_validate_vaccine_code_coding_code(self):
        """
        Test pre_validate_vaccine_code_coding_code accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="vaccineCode.coding[?(@.system=='http://snomed.info/sct')].code",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_vaccine_code_coding_display(self):
        """
        Test pre_validate_vaccine_code_coding_display accepts valid values and rejects invalid
        values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="vaccineCode.coding[?(@.system=='http://snomed.info/sct')].display",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_manufacturer_display(self):
        """
        Test pre_validate_manufacturer_display accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self, field_location="manufacturer.display", valid_strings_to_test=["dummy"]
        )

    def test_model_pre_validate_lot_number(self):
        """Test pre_validate_lot_number accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="lotNumber",
            valid_strings_to_test=["sample", "0123456789101112"],
            max_length=100,
            invalid_length_strings_to_test=InvalidValues.for_strings_with_max_100_chars,
        )

    def test_model_pre_validate_expiration_date(self):
        """Test pre_validate_expiration_date accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_date_value(
            self,
            field_location="expirationDate",
        )

    def test_model_pre_validate_site_coding(self):
        """Test pre_validate_site_coding accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_unique_list(
            self,
            field_location="site.coding",
            valid_lists_to_test=[[ValidValues.snomed_coding_element]],
            invalid_list_with_duplicates_to_test=[
                ValidValues.snomed_coding_element,
                ValidValues.snomed_coding_element,
            ],
            expected_error_message="site.coding[?(@.system=='http://snomed.info/sct')]"
            + " must be unique",
        )

    def test_model_pre_validate_site_coding_code(self):
        """Test pre_validate_site_coding_code accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="site.coding[?(@.system=='http://snomed.info/sct')].code",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_site_coding_display(self):
        """Test pre_validate_site_coding_display accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="site.coding[?(@.system=='http://snomed.info/sct')].display",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_route_coding(self):
        """Test pre_validate_route_coding accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_unique_list(
            self,
            field_location="route.coding",
            valid_lists_to_test=[[ValidValues.snomed_coding_element]],
            invalid_list_with_duplicates_to_test=[
                ValidValues.snomed_coding_element,
                ValidValues.snomed_coding_element,
            ],
            expected_error_message="route.coding[?(@.system=='http://snomed.info/sct')]"
            + " must be unique",
        )

    def test_model_pre_validate_route_coding_code(self):
        """Test pre_validate_route_coding_code accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="route.coding[?(@.system=='http://snomed.info/sct')].code",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_route_coding_display(self):
        """Test pre_validate_route_coding_display accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="route.coding[?(@.system=='http://snomed.info/sct')].display",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_dose_quantity_value(self):
        """Test pre_validate_dose_quantity_value accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_decimal_or_integer_value(
            self,
            field_location="doseQuantity.value",
            valid_decimals_and_integers_to_test=[
                1,  # small integer
                100,  # larger integer
                Decimal("1.0"),  # Only 0s after decimal point
                Decimal("0.1"),  # 1 decimal place
                Decimal("100.52"),  # 2 decimal places
                Decimal("32.430"),  # 3 decimal places
                Decimal("1.1234"),  # 4 decimal places,
            ],
            max_decimal_places=4,
        )

    def test_model_pre_validate_dose_quantity_code(self):
        """Test pre_validate_dose_quantity_code accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self, field_location="doseQuantity.code", valid_strings_to_test=["ABC123"]
        )

    def test_model_pre_validate_dose_quantity_unit(self):
        """Test pre_validate_dose_quantity_unit accepts valid values and rejects invalid values"""
        ValidatorModelTests.test_string_value(
            self,
            field_location="doseQuantity.unit",
            valid_strings_to_test=["Millilitre"],
        )

    # TODO: ?add extra reason code to sample data for validation testing
    def test_model_pre_validate_reason_code_codings(self):
        """Test pre_validate_reason_code_codings accepts valid values and rejects invalid values"""
        # Check that both of the 2 reasonCode[{index}].coding fields in the sample data are rejected
        # when invalid
        for i in range(1):
            ValidatorModelTests.test_list_value(
                self,
                field_location=f"reasonCode[{i}].coding",
                valid_lists_to_test=[[{"code": "ABC123", "display": "test"}]],
                predefined_list_length=1,
                valid_list_element={"code": "ABC123", "display": "test"},
            )

    # TODO: ?add extra reason code to sample data for validation testing
    def test_model_pre_validate_reason_code_coding_codes(self):
        """
        Test pre_validate_reason_code_coding_codes accepts valid values and rejects invalid values
        """
        # Check that both of the reasonCode[{index}].coding[0].code fields in the sample data are
        # rejected when invalid
        for i in range(1):
            ValidatorModelTests.test_string_value(
                self,
                field_location=f"reasonCode[{i}].coding[0].code",
                valid_strings_to_test=["ABC123"],
            )

    # TODO: ?add extra reason code to sample data for validation testing
    def test_model_pre_validate_reason_code_coding_displays(self):
        """
        Test pre_validate_reason_code_coding_displays accepts valid values and rejects invalid
        values
        """
        # Check that both of the reasonCode[{index}].coding[0].display fields in the sample data are
        # rejected when invalid
        for i in range(1):
            ValidatorModelTests.test_string_value(
                self,
                field_location=f"reasonCode[{i}].coding[0].display",
                valid_strings_to_test=["test"],
            )

    def test_model_pre_validate_patient_identifier_extension(self):
        """
        Test pre_validate_patient_identifier_extension accepts valid values and rejects invalid
        values
        """
        valid_patient_extension_item = {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "NHSNumberVerificationStatus",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-"
                        + "NHSNumberVerificationStatusEngland",
                        "code": "NHS_NUMBER_STATUS_INDICATOR_CODE",
                        "display": "NHS_NUMBER_STATUS_INDICATOR_DESCRIPTION",
                    }
                ]
            },
        }

        ValidatorModelTests.test_unique_list(
            self,
            field_location="contained[?(@.resourceType=='Patient')].identifier"
            + "[?(@.system=='https://fhir.nhs.uk/Id/nhs-number')].extension",
            valid_lists_to_test=[[valid_patient_extension_item]],
            invalid_list_with_duplicates_to_test=[
                valid_patient_extension_item,
                valid_patient_extension_item,
            ],
            expected_error_message="contained[?(@.resourceType=='Patient')].identifier"
            + "[?(@.system=='https://fhir.nhs.uk/Id/nhs-number')].extension[?(@.url=="
            + "'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "NHSNumberVerificationStatus')] must be unique",
        )

    def test_model_pre_validate_nhs_number_verification_status_coding(self):
        """
        Test pre_validate_nhs_number_verification_status_coding accepts valid values and rejects
        invalid values
        """
        valid_coding_item = {
            "system": "https://fhir.hl7.org.uk/CodeSystem"
            + "/UKCore-NHSNumberVerificationStatusEngland",
            "code": "NHS_NUMBER_STATUS_INDICATOR_CODE",
            "display": "NHS_NUMBER_STATUS_INDICATOR_DESCRIPTION",
        }

        ValidatorModelTests.test_unique_list(
            self,
            field_location="contained[?(@.resourceType=='Patient')].identifier"
            + "[?(@.system=='https://fhir.nhs.uk/Id/nhs-number')].extension[?(@.url=="
            + "'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "NHSNumberVerificationStatus')].valueCodeableConcept.coding",
            valid_lists_to_test=[[valid_coding_item]],
            invalid_list_with_duplicates_to_test=[
                valid_coding_item,
                valid_coding_item,
            ],
            expected_error_message="contained[?(@.resourceType=='Patient')].identifier"
            + "[?(@.system=='https://fhir.nhs.uk/Id/nhs-number')].extension[?(@.url=="
            + "'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "NHSNumberVerificationStatus')].valueCodeableConcept.coding"
            + "[?(@.system=='https://fhir.hl7.org.uk/CodeSystem/UKCore-"
            + "NHSNumberVerificationStatusEngland')] must be unique",
        )

    def test_model_pre_validate_nhs_number_verification_status_code(self):
        """
        Test pre_validate_nhs_number_verification_status_code accepts valid values and
        rejects invalid values
        """
        url = (
            "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "NHSNumberVerificationStatus"
        )
        system = "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland"
        field_type = "code"

        field_location = (
            "contained[?(@.resourceType=='Patient')].identifier"
            + "[?(@.system=='https://fhir.nhs.uk/Id/nhs-number')]."
            + generate_field_location_for_extension(url, system, field_type)
        )
        ValidatorModelTests.test_string_value(
            self,
            field_location,
            valid_strings_to_test=["01"],
        )

    def test_model_pre_validate_nhs_number_verification_status_display(self):
        """
        Test pre_validate_nhs_number_verification_status_display accepts valid values and
        rejects invalid values
        """
        url = (
            "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "NHSNumberVerificationStatus"
        )
        system = "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland"
        field_type = "display"

        field_location = (
            "contained[?(@.resourceType=='Patient')].identifier"
            + "[?(@.system=='https://fhir.nhs.uk/Id/nhs-number')]."
            + generate_field_location_for_extension(url, system, field_type)
        )
        ValidatorModelTests.test_string_value(
            self,
            field_location,
            valid_strings_to_test=["01"],
        )

    def test_model_pre_validate_organisation_identifier_system(self):
        """
        Test pre_validate_organization_identifier_system accepts valid systems and rejects invalid
        systems
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="performer[?(@.actor.type=='Organization')].actor.identifier.system",
            valid_strings_to_test=["DUMMY"],
        )

    def test_model_pre_validate_local_patient_value(self):
        """
        Test pre_validate_local_patient_value accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='LocalPatient')].answer[0].valueReference.identifier.value",
            valid_strings_to_test=[
                "ACME-patient123456",
                "ACME-CUST1-pat123456",
                "ACME-CUST2-pat123456",
            ],
            invalid_length_strings_to_test=["ACME-CUST1-pat1234567"],
            max_length=20,
        )

    def test_model_pre_validate_local_patient_system(self):
        """
        Test pre_validate_local_patient_system accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='LocalPatient')].answer[0].valueReference.identifier.system",
            valid_strings_to_test=["https://supplierABC/identifiers"],
        )

    def test_model_pre_validate_consent_code(self):
        """
        Test pre_validate_consent_code accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='Consent')].answer[0].valueCoding.code",
            valid_strings_to_test=["snomed"],
        )

    def test_model_pre_validate_consent_display(self):
        """
        Test pre_validate_consent_display accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='Consent')].answer[0].valueCoding.display",
            valid_strings_to_test=[
                "Patient consented to be given the vaccination",
                "Parent/carer/guardian consented for child to be given the vaccination",
            ],
        )

    def test_model_pre_validate_care_setting_code(self):
        """
        Test pre_validate_care_setting_code accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='CareSetting')].answer[0].valueCoding.code",
            valid_strings_to_test=["snomed"],
        )

    def test_model_pre_validate_care_setting_display(self):
        """
        Test pre_validate_care_setting_display accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='CareSetting')].answer[0].valueCoding.display",
            valid_strings_to_test=[
                "SNOMED-CT Term description Community health services (qualifier value)"
            ],
        )

    def test_model_pre_validate_ip_address(self):
        """
        Test pre_validate_ip_address accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='IpAddress')].answer[0].valueString",
            valid_strings_to_test=[
                "192.168.0.1",
                "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            ],
        )

    def test_model_pre_validate_user_id(self):
        """
        Test pre_validate_user_id accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='UserId')].answer[0].valueString",
            valid_strings_to_test=["LESTER_TESTER-1234"],
        )

    def test_model_pre_validate_user_name(self):
        """
        Test pre_validate_user_name accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='UserName')].answer[0].valueString",
            valid_strings_to_test=["LESTER TESTER"],
        )

    def test_model_pre_validate_user_email(self):
        """
        Test pre_validate_user_email accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='UserEmail')].answer[0].valueString",
            valid_strings_to_test=["lester.tester@test.com"],
        )

    def test_model_pre_validate_submitted_time_stamp(self):
        """
        Test pre_validate_submitted_time_stamp accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_date_time_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='SubmittedTimeStamp')].answer[0].valueDateTime",
        )

    def test_model_pre_validate_location_identifier_value(self):
        """
        Test pre_validate_location_identifier_value accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="location.identifier.value",
            valid_strings_to_test=["B0C4P", "140565"],
        )

    def test_model_pre_validate_location_identifier_system(self):
        """
        Test pre_validate_location_identifier_system accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="location.identifier.system",
            valid_strings_to_test=["https://fhir.hl7.org.uk/Id/140565"],
        )

    def test_model_pre_validate_reduce_validation(self):
        """
        Test pre_validate_reduce_validation accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_boolean_value(
            self,
            field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='ReduceValidation')].answer[0].valueBoolean",
        )


class TestImmunizationModelPreValidationRulesForNotDone(unittest.TestCase):
    """Test immunization pre validation rules on the FHIR model using the status="not-done" data"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample immunization event JSON data
        cls.immunization_file_path = (
            f"{cls.data_path}/sample_immunization_not_done_event.json"
        )
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f, parse_float=Decimal)

        # set up the untouched sample immunization event JSON data
        cls.untouched_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = ImmunizationValidator()
        cls.validator.add_custom_root_pre_validators()

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_json_data, self.json_data)

    def test_model_pre_validate_vaccination_situation_code(self):
        """
        Test pre_validate_vaccination_situation_code accepts valid values and rejects invalid
        values
        """

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
            system="http://snomed.info/sct",
            field_type="code",
        )

        ValidatorModelTests.test_string_value(
            self, field_location=field_location, valid_strings_to_test=["dummy"]
        )

    def test_model_pre_validate_vaccination_situation_display(self):
        """
        Test pre_validate_vaccination_situation_display accepts valid values and rejects invalid
        values
        """

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
            system="http://snomed.info/sct",
            field_type="display",
        )

        ValidatorModelTests.test_string_value(
            self, field_location=field_location, valid_strings_to_test=["dummy"]
        )

    def test_model_pre_validate_status_reason_coding(self):
        """
        Test pre_validate_status_reason_coding accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_unique_list(
            self,
            field_location="statusReason.coding",
            valid_lists_to_test=[[ValidValues.snomed_coding_element]],
            invalid_list_with_duplicates_to_test=[
                ValidValues.snomed_coding_element,
                ValidValues.snomed_coding_element,
            ],
            expected_error_message="statusReason.coding[?(@.system=='http://snomed.info/sct')]"
            + " must be unique",
        )

    def test_model_pre_validate_status_reason_coding_code(self):
        """
        Test pre_validate_status_reason_coding_code accepts valid values and rejects invalid values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="statusReason.coding[?(@.system=='http://snomed.info/sct')].code",
            valid_strings_to_test=["dummy"],
        )

    def test_model_pre_validate_status_reason_coding_display(self):
        """
        Test pre_validate_status_reason_coding_display accepts valid values and rejects invalid
        values
        """
        ValidatorModelTests.test_string_value(
            self,
            field_location="statusReason.coding[?(@.system=='http://snomed.info/sct')].display",
            valid_strings_to_test=["dummy"],
        )


# class TestImmunizationModelPreValidationRulesForReduceValidation(unittest.TestCase):
#     """
#     Test immunization pre validation rules on the FHIR model using the status="reduce validation"
#     data
#     """

#     @classmethod
#     def setUpClass(cls):
#         """Set up for the tests. This only runs once when the class is instantiated"""
#         # Set up the path for the sample data
#         cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

#         # set up the sample immunization event JSON data
#         cls.immunization_file_path = (
#             f"{cls.data_path}/sample_immunization_reduce_validation_event.json"
#         )
#         with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
#             cls.json_data = json.load(f, parse_float=Decimal)

#         # set up the untouched sample immunization event JSON data
#         cls.untouched_json_data = deepcopy(cls.json_data)

#         # set up the validator and add custom root validators
#         cls.validator = ImmunizationValidator()
#         cls.validator.add_custom_root_pre_validators()

#     def setUp(self):
#         """Set up for each test. This runs before every test"""
#         # Ensure that good data is not inadvertently amended by the tests
#         self.assertEqual(self.untouched_json_data, self.json_data)

#         # TODO: Create separate validation rule to check reduce validation field only and
#         # not apply validation if this is true

#     # def test_model_pre_validate_reduce_validation_reason_answer(self):
#     #     """
#     #     Test pre_validate_reduce_validation_display accepts valid values and rejects invalid values
#     #     """
#     #     ValidatorModelTests.test_string_value(
#     #         self,
#     #         field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
#     #         + ".item[?(@.linkId=='ReduceValidationReason')].answer[0].valueString",
#     #         valid_strings_to_test=["From DPS CSV"],
#     #     )
