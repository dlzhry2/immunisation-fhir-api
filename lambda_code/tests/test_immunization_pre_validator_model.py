"""Test immunization pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from decimal import Decimal

from models.fhir_immunization import ImmunizationValidator
from .utils import (
    ValidatorModelTests,
    ValidValues,
    InvalidValues,
    generate_field_location_for_questionnnaire_response,
    generate_field_location_for_extension,
)


class TestImmunizationModelPreValidationRules(unittest.TestCase):
    """Test immunization pre validation rules on the model"""

    @classmethod
    def setUpClass(cls):
        """Set up for the tests. This only runs once when the class is instantiated"""
        # Set up the path for the sample data
        cls.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample immunization event JSON data
        cls.immunization_file_path = f"{cls.data_path}/sample_immunization_event.json"
        with open(cls.immunization_file_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f, parse_float=Decimal)

        # set up the untouched sample immunization event JSON data
        cls.untouched_json_data = deepcopy(cls.json_data)

        # set up the validator and add custom root validators
        cls.validator = ImmunizationValidator()
        cls.validator.add_custom_root_validators()

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Ensure that good data is not inadvertently amended by the tests
        self.assertEqual(self.untouched_json_data, self.json_data)

    def test_model_pre_validate_valid_patient_identifier_value(self):
        """Test pre_validate_patient_identifier_value accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="patient.identifier.value",
            valid_values_to_test=["1234567890"],
        )

    def test_model_pre_validate_invalid_patient_identifier_value(self):
        """Test pre_validate_patient_identifier_value rejects invalid values when in a model"""
        # Test invalid data types and invalid length strings
        ValidatorModelTests.string_invalid(
            self,
            field_location="patient.identifier.value",
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

    def test_model_pre_validate_valid_occurrence_date_time(self):
        """Test pre_validate_occurrence_date_time accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="occurrenceDateTime",
            valid_values_to_test=ValidValues.for_date_times,
        )

    def test_model_pre_validate_invalid_occurrence_date_time(self):
        """Test pre_validate_occurrence_date_time rejects invalid values when in a model"""
        ValidatorModelTests.date_time_invalid(
            self,
            field_location="occurrenceDateTime",
            is_occurrence_date_time=True,
        )

    def test_model_pre_validate_valid_contained(self):
        """Test pre_validate_contained accepts valid values when in a model"""
        valid_items_to_test = [
            [{"resourceType": "QuestionnaireResponse", "status": "completed"}]
        ]

        ValidatorModelTests.valid(
            self,
            field_location="contained",
            valid_values_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_contained(self):
        """Test pre_validate_contained rejects invalid values when in a model"""
        valid_list_element = {
            "resourceType": "QuestionnaireResponse",
            "status": "completed",
        }

        ValidatorModelTests.list_invalid(
            self,
            field_location="contained",
            predefined_list_length=1,
            valid_list_element=valid_list_element,
        )

    def test_model_pre_validate_valid_questionnaire_answers(self):
        """Test pre_validate_questionnaire_answers accepts valid values when in a model"""
        # Check that all of the 12 answer fields in the sample data are accepted when valid
        for i in range(12):
            ValidatorModelTests.valid(
                self,
                field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
                + f".item[{i}].answer",
                valid_values_to_test=[[{"valueCoding": {"code": "B0C4P"}}]],
            )

    def test_model_pre_validate_invalid_questionnaire_answers(self):
        """Test pre_validate_quesionnaire_answers rejects invalid values when in a model"""
        # Check that any of the 12 answer fields in the sample data are rejected when invalid
        for i in range(12):
            ValidatorModelTests.list_invalid(
                self,
                field_location="contained[?(@.resourceType=='QuestionnaireResponse')]"
                + f".item[{i}].answer",
                predefined_list_length=1,
                valid_list_element={"valueCoding": {"code": "B0C4P"}},
            )

    def test_model_pre_validate_valid_questionnaire_site_code_code(self):
        """Test pre_validate_questionnaire_site_code_code accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location=generate_field_location_for_questionnnaire_response(
                link_id="SiteCode", field_type="code"
            ),
            valid_values_to_test=["B0C4P"],
        )

    def test_model_pre_validate_invalid_questionnaire_site_code_code(self):
        """Test pre_validate_questionnaire_site_code_code rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self,
            field_location=generate_field_location_for_questionnnaire_response(
                link_id="SiteCode", field_type="code"
            ),
        )

    def test_model_pre_validate_valid_site_name_code(self):
        """Test pre_validate_site_name_code accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location=generate_field_location_for_questionnnaire_response(
                link_id="SiteName", field_type="code"
            ),
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_site_name_code(self):
        """Test pre_validate_site_code_code rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self,
            field_location=generate_field_location_for_questionnnaire_response(
                link_id="SiteName", field_type="code"
            ),
        )

    def test_model_pre_validate_valid_identifier(self):
        """Test pre_validate_identifier accepts valid values when in a model"""
        valid_items_to_test = [
            [
                {
                    "system": "https://supplierABC/identifiers/vacc",
                    "value": "ACME-vacc123456",
                }
            ],
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
        ValidatorModelTests.string_invalid(
            self,
            field_location="identifier[0].value",
        )

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
        ValidatorModelTests.string_invalid(
            self,
            field_location="identifier[0].system",
        )

    def test_model_pre_validate_valid_status(self):
        """Test pre_validate_status accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="status",
            valid_values_to_test=["completed", "entered-in-error", "not-done"],
        )

    def test_model_pre_validate_invalid_status(self):
        """Test pre_validate_status rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self,
            field_location="status",
            predefined_values=("completed", "entered-in-error", "not-done"),
            invalid_strings_to_test=["1", "complete", "enteredinerror"],
            is_mandatory_fhir=True,
        )

    def test_model_pre_validate_valid_recorded(self):
        """Test pre_validate_recorded accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="recorded",
            valid_values_to_test=["2000-01-01", "1933-12-31"],
        )

    def test_model_pre_validate_invalid_recorded(self):
        """Test pre_validate_recorded rejects invalid values when in a model"""
        ValidatorModelTests.date_invalid(self, field_location="recorded")

    def test_model_pre_validate_valid_primary_source(self):
        """Test pre_validate_primary_source accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="primarySource",
            valid_values_to_test=[True, False],
        )

    def test_model_pre_validate_invalid_primary_source(self):
        """Test pre_validate_primary_source rejects invalid values when in a model"""
        ValidatorModelTests.boolean_invalid(self, field_location="primarySource")

    def test_model_pre_validate_valid_report_origin_text(self):
        """Test pre_validate_report_origin_text accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="reportOrigin.text",
            valid_values_to_test=[
                "sample",
                "Free text description of organisation recording the event",
            ],
        )

    def test_model_pre_validate_invalid_report_origin_text(self):
        """Test pre_validate_report_origin_text rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self,
            field_location="reportOrigin.text",
            max_length=100,
            invalid_length_strings_to_test=InvalidValues.for_strings_with_max_100_chars,
        )

    def test_model_pre_validate_valid_extension_value_codeable_concept_codings(self):
        """
        Test pre_validate_extension_value_codeable_concept_codings accepts valid values when in a
        model
        """
        # Check that both of the relevant coding fields in the sample data are accepted when valid
        for i in range(2):
            ValidatorModelTests.valid(
                self,
                field_location=f"extension[{i}].valueCodeableConcept.coding",
                valid_values_to_test=[[ValidValues.snomed_coding_element]],
            )

    def test_model_pre_validate_invalid_extension_value_codeable_concept_codings(self):
        """
        Test pre_validate_extension_value_codeable_concept_codings rejects invalid values when
        in a model
        """
        # Check that both of the 2 relevant coding fields in the sample data are rejected when
        # invalid
        for i in range(2):
            ValidatorModelTests.list_invalid(
                self,
                field_location=f"extension[{i}].valueCodeableConcept.coding",
                predefined_list_length=1,
                valid_list_element=ValidValues.snomed_coding_element,
            )

    def test_model_pre_validate_valid_vaccination_procedure_code(self):
        """Test pre_validate_vaccination_procedure_code accepts valid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
            field_type="code",
        )

        ValidatorModelTests.valid(
            self,
            field_location=field_location,
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_vaccination_procedure_code(self):
        """Test pre_validate_vaccination_procedure_code rejects invalid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
            field_type="code",
        )

        ValidatorModelTests.string_invalid(
            self,
            field_location=field_location,
        )

    def test_model_pre_validate_valid_vaccination_procedure_display(self):
        """Test pre_validate_vaccination_procedure_display accepts valid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
            field_type="display",
        )

        ValidatorModelTests.valid(
            self,
            field_location=field_location,
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_vaccination_procedure_display(self):
        """Test pre_validate_vaccination_procedure_display rejects invalid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
            field_type="display",
        )

        ValidatorModelTests.string_invalid(
            self,
            field_location=field_location,
        )

    def test_model_pre_validate_valid_vaccination_situation_code(self):
        """Test pre_validate_vaccination_situation_code accepts valid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
            field_type="code",
        )

        ValidatorModelTests.valid(
            self,
            field_location=field_location,
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_vaccination_situation_code(self):
        """Test pre_validate_vaccination_situation_code rejects invalid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
            field_type="code",
        )

        ValidatorModelTests.string_invalid(
            self,
            field_location=field_location,
        )

    def test_model_pre_validate_valid_vaccination_situation_display(self):
        """Test pre_validate_vaccination_situation_display accepts valid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
            field_type="display",
        )

        ValidatorModelTests.valid(
            self,
            field_location=field_location,
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_vaccination_situation_display(self):
        """Test pre_validate_vaccination_situation_display rejects invalid values when in a model"""

        field_location = generate_field_location_for_extension(
            url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
            field_type="display",
        )

        ValidatorModelTests.string_invalid(
            self,
            field_location=field_location,
        )

    def test_model_pre_validate_valid_status_reason_coding(self):
        """Test pre_validate_status_reason_coding accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="statusReason.coding",
            valid_values_to_test=[[ValidValues.snomed_coding_element]],
        )

    def test_model_pre_validate_invalid_status_reason_coding(self):
        """Test pre_validate_status_reason_coding rejects invalid values when in a model"""
        ValidatorModelTests.list_invalid(
            self,
            field_location="statusReason.coding",
            predefined_list_length=1,
            valid_list_element=ValidValues.snomed_coding_element,
        )

    def test_model_pre_validate_valid_status_reason_coding_code(self):
        """Test pre_validate_status_reason_coding_code accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="statusReason.coding[0].code",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_status_reason_coding_code(self):
        """Test pre_validate_status_reason_coding_code rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self,
            field_location="statusReason.coding[0].code",
        )

    def test_model_pre_validate_valid_status_reason_coding_display(self):
        """Test pre_validate_status_reason_coding_display accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="statusReason.coding[0].display",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_status_reason_coding_display(self):
        """Test pre_validate_status_reason_coding_display rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self, field_location="statusReason.coding[0].display"
        )

    def test_model_pre_validate_valid_protocol_applied(self):
        """Test pre_validate_protocol_applied accepts valid values when in a model"""
        valid_items_to_test = [
            [
                {
                    "targetDisease": [
                        {"coding": [{"code": "ABC123"}]},
                        {"coding": [{"code": "DEF456"}]},
                    ],
                    "doseNumberPositiveInt": 1,
                },
            ]
        ]
        ValidatorModelTests.valid(
            self,
            field_location="protocolApplied",
            valid_values_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_protocol_applied(self):
        """Test pre_validate_protocol_applied rejects invalid values when in a model"""
        valid_list_element = {
            "targetDisease": [
                {"coding": [{"code": "ABC123"}]},
                {"coding": [{"code": "DEF456"}]},
            ],
            "doseNumberPositiveInt": 1,
        }

        ValidatorModelTests.list_invalid(
            self,
            field_location="protocolApplied",
            predefined_list_length=1,
            valid_list_element=valid_list_element,
        )

    def test_model_pre_validate_valid_protocol_applied_dose_number_positive_int(
        self,
    ):
        """
        Test pre_validate_protocol_applied_dose_number_positive_int accepts valid values when
        in a model
        """
        ValidatorModelTests.valid(
            self,
            field_location="protocolApplied[0].doseNumberPositiveInt",
            valid_values_to_test=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        )

    def test_model_pre_validate_invalid_protocol_applied_dose_number_positive_int(
        self,
    ):
        """
        Test pre_validate_protocol_applied_dose_number_positive_int rejects invalid values when in a
        model
        """
        # Test invalid data types and non-positive integers
        ValidatorModelTests.positive_integer_invalid(
            self, field_location="protocolApplied[0].doseNumberPositiveInt", max_value=9
        )

    def test_model_pre_validate_valid_vaccine_code_coding(self):
        """Test pre_validate_vaccine_code_coding accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="vaccineCode.coding",
            valid_values_to_test=[[ValidValues.snomed_coding_element]],
        )

    def test_model_pre_validate_invalid_vaccine_code_coding(self):
        """Test pre_validate_vaccine_code_coding rejects invalid values when in a model"""
        ValidatorModelTests.list_invalid(
            self,
            field_location="vaccineCode.coding",
            predefined_list_length=1,
            valid_list_element=ValidValues.snomed_coding_element,
        )

    def test_model_pre_validate_valid_vaccine_code_coding_code(self):
        """Test pre_validate_vaccine_code_coding_code accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="vaccineCode.coding[0].code",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_vaccine_code_coding_code(self):
        """Test pre_validate_vaccine_code_coding_code rejects invalid values when in a model"""

        ValidatorModelTests.string_invalid(
            self, field_location="vaccineCode.coding[0].code"
        )

    def test_model_pre_validate_valid_vaccine_code_coding_display(self):
        """Test pre_validate_vaccine_code_coding_display accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="vaccineCode.coding[0].display",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_vaccine_code_coding_display(self):
        """Test pre_validate_vaccine_code_coding_display rejects invalid values when in a model"""

        ValidatorModelTests.string_invalid(
            self, field_location="vaccineCode.coding[0].display"
        )

    def test_model_pre_validate_valid_manufacturer_display(self):
        """Test pre_validate_manufacturer_display accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="manufacturer.display",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_manufacturer_display(self):
        """Test pre_validate_manufacturer_display rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="manufacturer.display")

    def test_model_pre_validate_valid_lot_number(self):
        """Test pre_validate_lot_number accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="lotNumber",
            valid_values_to_test=["sample", "0123456789101112"],
        )

    def test_model_pre_validate_invalid_lot_number(self):
        """Test pre_validate_lot_number rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self,
            field_location="lotNumber",
            max_length=100,
            invalid_length_strings_to_test=InvalidValues.for_strings_with_max_100_chars,
        )

    def test_model_pre_validate_valid_expiration_date(self):
        """Test pre_validate_expiration_date accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="expirationDate",
            valid_values_to_test=["2030-01-01", "2003-12-31"],
        )

    def test_model_pre_validate_invalid_expiration_date(self):
        """Test pre_validate_expiration_date rejects invalid values when in a model"""
        ValidatorModelTests.date_invalid(
            self,
            field_location="expirationDate",
        )

    def test_model_pre_validate_valid_site_coding(self):
        """Test pre_validate_site_coding accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="site.coding",
            valid_values_to_test=[[ValidValues.snomed_coding_element]],
        )

    def test_model_pre_validate_invalid_site_coding(self):
        """Test pre_validate_site_coding rejects invalid values when in a model"""
        ValidatorModelTests.list_invalid(
            self,
            field_location="site.coding",
            predefined_list_length=1,
            valid_list_element=ValidValues.snomed_coding_element,
        )

    def test_model_pre_validate_valid_site_coding_code(self):
        """Test pre_validate_site_coding_code accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="site.coding[0].code",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_site_coding_code(self):
        """Test pre_validate_site_coding_code rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="site.coding[0].code")

    def test_model_pre_validate_valid_site_coding_display(self):
        """Test pre_validate_site_coding_display accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="site.coding[0].display",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_site_coding_display(self):
        """Test pre_validate_site_coding_display rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(
            self, field_location="site.coding[0].display"
        )

    def test_model_pre_validate_valid_route_coding(self):
        """Test pre_validate_route_coding accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="route.coding",
            valid_values_to_test=[[ValidValues.snomed_coding_element]],
        )

    def test_model_pre_validate_invalid_route_coding(self):
        """Test pre_validate_route_coding rejects invalid values when in a model"""
        ValidatorModelTests.list_invalid(
            self,
            field_location="route.coding",
            predefined_list_length=1,
            valid_list_element=ValidValues.snomed_coding_element,
        )

    def test_model_pre_validate_valid_route_coding_code(self):
        """Test pre_validate_route_coding_code accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="route.coding[0].code",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_route_coding_code(self):
        """Test pre_validate_route_coding_code rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="route.coding[0].code")

    def test_model_pre_validate_valid_route_coding_display(self):
        """Test pre_validate_route_coding_display accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="route.coding[0].display",
            valid_values_to_test=["dummy"],
        )

    def test_model_pre_validate_invalid_route_coding_display(self):
        """Test pre_validate_route_coding_display rejects invalid values when in a model"""

        ValidatorModelTests.string_invalid(
            self, field_location="route.coding[0].display"
        )

    def test_model_pre_validate_valid_dose_quantity_value(self):
        """Test pre_validate_dose_quantity_value accepts valid values when in a model"""
        valid_items_to_test = [
            1,  # small integer
            100,  # larger integer
            Decimal("1.0"),  # Only 0s after decimal point
            Decimal("0.1"),  # 1 decimal place
            Decimal("100.52"),  # 2 decimal places
            Decimal("32.430"),  # 3 decimal places
            Decimal("1.1234"),  # 4 decimal places,
        ]

        ValidatorModelTests.valid(
            self,
            field_location="doseQuantity.value",
            valid_values_to_test=valid_items_to_test,
        )

    def test_model_pre_validate_invalid_dose_quantity_value(self):
        """Test pre_validate_dose_quantity_value rejects invalid values when in a model"""
        ValidatorModelTests.decimal_or_integer_invalid(
            self, field_location="doseQuantity.value", max_decimal_places=4
        )

    def test_model_pre_validate_valid_dose_quantity_code(self):
        """Test pre_validate_dose_quantity_code accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="doseQuantity.code",
            valid_values_to_test=["ABC123"],
        )

    def test_model_pre_validate_invalid_dose_quantity_code(self):
        """Test pre_validate_dose_quantity_code rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="doseQuantity.code")

    def test_model_pre_validate_valid_dose_quantity_unit(self):
        """Test pre_validate_dose_quantity_unit accepts valid values when in a model"""
        ValidatorModelTests.valid(
            self,
            field_location="doseQuantity.unit",
            valid_values_to_test=["Millilitre"],
        )

    def test_model_pre_validate_invalid_dose_quantity_unit(self):
        """Test pre_validate_dose_quantity_unit rejects invalid values when in a model"""
        ValidatorModelTests.string_invalid(self, field_location="doseQuantity.unit")

    def test_model_pre_validate_valid_reason_code_codings(self):
        """Test pre_validate_reason_code_codings accepts valid values when in a model"""
        valid_items_to_test = [[{"code": "ABC123", "display": "test"}]]
        # Check that both of the reasonCode[{index}].coding fields in the sample data are accepted
        # when valid
        for i in range(2):
            ValidatorModelTests.valid(
                self,
                field_location=f"reasonCode[{i}].coding",
                valid_values_to_test=valid_items_to_test,
            )

    def test_model_pre_validate_invalid_reason_code_codings(self):
        """Test pre_validate_reason_code_codings rejects invalid values when in a model"""
        # Check that both of the 2 reasonCode[{index}].coding fields in the sample data are rejected
        # when invalid
        for i in range(2):
            ValidatorModelTests.list_invalid(
                self,
                field_location=f"reasonCode[{i}].coding",
                predefined_list_length=1,
                valid_list_element={"code": "ABC123", "display": "test"},
            )

    def test_model_pre_validate_valid_reason_code_coding_codes(self):
        """Test pre_validate_reason_code_coding_codes accepts valid values when in a model"""
        # Check that both of the reasonCode[{index}].coding[0].code fields in the sample data are
        # accepted when valid
        for i in range(2):
            ValidatorModelTests.valid(
                self,
                field_location=f"reasonCode[{i}].coding[0].code",
                valid_values_to_test=["ABC123"],
            )

    def test_model_pre_validate_invalid_reason_code_coding_codes(self):
        """Test pre_validate_reason_code_coding_codes rejects invalid values when in a model"""
        # Check that both of the reasonCode[{index}].coding[0].code fields in the sample data are
        # rejected when invalid
        for i in range(2):
            ValidatorModelTests.string_invalid(
                self, field_location=f"reasonCode[{i}].coding[0].code"
            )

    def test_model_pre_validate_valid_reason_code_coding_displays(self):
        """Test pre_validate_reason_code_coding_displays accepts valid values when in a model"""
        # Check that both of the reasonCode[{index}].coding[0].display fields in the sample data are
        # accepted when valid
        for i in range(2):
            ValidatorModelTests.valid(
                self,
                field_location=f"reasonCode[{i}].coding[0].display",
                valid_values_to_test=["ABC123"],
            )

    def test_model_pre_validate_invalid_reason_code_coding_displays(self):
        """Test pre_validate_reason_code_coding_displays rejects invalid values when in a model"""
        # Check that both of the reasonCode[{index}].coding[0].display fields in the sample data are
        # rejected when invalid
        for i in range(2):
            ValidatorModelTests.string_invalid(
                self, field_location=f"reasonCode[{i}].coding[0].display"
            )
