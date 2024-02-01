"""Test immunization pre validation rules on the model"""
import unittest
import os
import json
from copy import deepcopy
from decimal import Decimal
from jsonpath_ng.ext import parse
from models.fhir_immunization import ImmunizationValidator
from .utils.generic_utils import (
    generate_field_location_for_questionnnaire_response,
    generate_field_location_for_extension,
    # these have an underscore to avoid pytest collecting them as tests
    test_valid_values_accepted as _test_valid_values_accepted,
    test_invalid_values_rejected as _test_invalid_values_rejected,
)
from .utils.mandation_test_utils import MandationTests


class TestImmunizationModelPostValidationRules(unittest.TestCase):
    """Test immunization post validation rules on the FHIR model"""

    def setUp(self):
        """Set up for each test. This runs before every test"""
        # Set up the path for the sample data
        self.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"

        # set up the sample immunization event JSON data
        self.immunization_file_path = (
            f"{self.data_path}/sample_covid_immunization_event.json"
        )
        with open(self.immunization_file_path, "r", encoding="utf-8") as f:
            self.json_data = json.load(f, parse_float=Decimal)

        # set up the validator and add custom root validators
        self.validator = ImmunizationValidator()
        self.validator.add_custom_root_pre_validators()
        self.validator.add_custom_root_post_validators()

    def test_model_post_reduce_validation(self):
        """Test set_reduce_validation"""
        valid_json_data = deepcopy(self.json_data)
        field_location = (
            "contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='ReduceValidation')].answer[0].valueBoolean"
        )

        # Test that reduce_validation_code property is set to the value of
        # reduce_validation_code in the JSON data, where it exists
        for valid_value in [True, False]:
            valid_json_data = parse(field_location).update(valid_json_data, valid_value)
            self.validator.validate(valid_json_data)
            self.assertEqual(
                valid_value, self.validator.immunization.reduce_validation_code
            )

        # Test that reduce_validation_code property is set as False, when there is no
        # reduce_validation_code in the JSON data
        valid_json_data = parse(field_location).filter(lambda d: True, valid_json_data)
        self.validator.validate(valid_json_data)
        self.assertEqual(False, self.validator.immunization.reduce_validation_code)

    def test_model_post_vaccination_procedure_code(self):
        """
        Test validate_and_set_vaccination_procedure_code accepts valid values, rejects invalid
        values and rejects missing data
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = (
            "extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/"
            + "Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[?(@.system=="
            + "'http://snomed.info/sct')].code"
        )

        # Test that a valid COVID-19 code is accepted and vaccine_type is therefore set to COVID-19
        _test_valid_values_accepted(
            self,
            valid_json_data=valid_json_data,
            field_location=field_location,
            valid_values_to_test=["1324681000000101"],
        )
        self.assertEqual("COVID-19", self.validator.immunization.vaccine_type)

        # Test that an invalid code is rejected
        _test_invalid_values_rejected(
            self,
            valid_json_data=valid_json_data,
            field_location=field_location,
            invalid_value="INVALID_VALUE",
            expected_error_message=f"{field_location}:"
            + " INVALID_VALUE is not a valid code for this service",
            expected_error_type="value_error",
        )

        # Test that json data which doesn't contain vaccination_procedure_code is rejected
        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data=valid_json_data,
            field_location=field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )

    def test_model_post_status(self):
        """
        Test that when status field is absent it is rejected (by FHIR validator) and when it is
        present the status property is set equal to it
        """
        valid_json_data = deepcopy(self.json_data)

        # Test that status property is set to the value of status in the JSON data, where it exists
        for valid_value in ["completed", "entered-in-error", "not-done"]:
            valid_json_data = parse("status").update(valid_json_data, valid_value)
            self.validator.validate(valid_json_data)
            self.assertEqual(valid_value, self.validator.immunization.status)

        # This error is raised by the FHIR validator (status is a mandatory FHIR field)
        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data=valid_json_data,
            field_location="status",
            expected_error_message="field required",
            expected_error_type="value_error.missing",
            is_mandatory_fhir=True,
        )

    def test_model_post_patient_identifier_value(self):
        """
        Test that the JSON data is accepted whether or not it contains
        contained[?(@.resourceType=='Patient')].identifier[0].value
        """
        valid_json_data = deepcopy(self.json_data)

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self,
            valid_json_data,
            field_location="contained[?(@.resourceType=='Patient')].identifier[0].value",
        )

    def test_model_post_occurrence_date_time(self):
        """
        Test that the JSON data is accepted if it contains occurrenceDateTime and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "occurrenceDateTime"

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        # This error is raised by the FHIR validator (occurrenceDateTime is a mandatory FHIR field)
        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data,
            field_location,
            expected_error_message="Expect any of field value from this list ['occurrenceDateTime',"
            + " 'occurrenceString'].",
            expected_error_type="value_error",
            is_mandatory_fhir=True,
        )

    def test_model_post_organization_identifier_value(self):
        """
        Test that the JSON data is accepted if it contains
        performer[?(@.actor.type=='Organization').identifier.value] and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = (
            "performer[?(@.actor.type=='Organization')].actor.identifier.value"
        )

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data,
            field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )

    def test_model_post_organization_display(self):
        """
        Test that the JSON data is accepted if it contains
        performer[?(@.actor.type=='Organization')].actor.display and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "performer[?(@.actor.type=='Organization')].actor.display"

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data,
            field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )

    def test_model_post_identifer_value(self):
        """
        Test that the JSON data is accepted if it contains identifier[0].value and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "identifier[0].value"

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data,
            field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )

    def test_model_post_identifer_system(self):
        """
        Test that the JSON data is accepted if it contains identifier[0].system and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "identifier[0].system"

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data,
            field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )

    def test_model_post_recorded(self):
        """
        Test that the JSON data is accepted if it contains recorded and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "recorded"

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data,
            field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )

    def test_model_post_primary_source(self):
        """
        Test that the JSON data is accepted if it contains primarySource and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "primarySource"

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data,
            field_location,
            expected_error_message=f"{field_location} is a mandatory field",
            expected_error_type="value_error",
        )

    def test_model_post_report_origin_text(self):
        """
        Test that the JSON data is accepted if it contains reportOrigin.text and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "reportOrigin.text"

        # Test no errors are raised when primarySource is True
        json_data_with_primary_source_true = parse("primarySource").update(
            deepcopy(valid_json_data), True
        )

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, json_data_with_primary_source_true
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, json_data_with_primary_source_true, field_location
        )

        # Test field is present when primarySource is False
        json_data_with_primary_source_false = parse("primarySource").update(
            deepcopy(valid_json_data), False
        )

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, json_data_with_primary_source_false
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            json_data_with_primary_source_false,
            field_location,
            expected_error_message=f"{field_location} is mandatory when primarySource is false",
            expected_error_type="MandatoryError",
        )
