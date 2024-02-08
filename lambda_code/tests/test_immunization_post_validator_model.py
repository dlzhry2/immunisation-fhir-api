"""Test immunization pre validation rules on the model"""

import unittest
import os
import json
from copy import deepcopy
from decimal import Decimal
from jsonpath_ng.ext import parse
from models.fhir_immunization import ImmunizationValidator
from .utils.generic_utils import (
    # these have an underscore to avoid pytest collecting them as tests
    test_valid_values_accepted as _test_valid_values_accepted,
    test_invalid_values_rejected as _test_invalid_values_rejected,
    load_json_data_for_tests,
)
from .utils.mandation_test_utils import MandationTests


class TestImmunizationModelPostValidationRulesValidData(unittest.TestCase):
    """Test that each piece of valid sample data passes post validation"""

    def test_sample_data(self):
        """Test that each piece of valid sample data passes post validation"""
        data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"
        # TODO: Clarify rules to allow all commented out files to pass
        files_to_test = [
            "sample_covid_immunization_event.json",
            "sample_flu_immunization_event.json",
            # # "sample_immunization_not_done_event.json",
            "sample_immunization_reduce_validation_event.json",
        ]

        for file in files_to_test:
            with open(f"{data_path}/{file}", "r", encoding="utf-8") as f:
                valid_json_data = json.load(f, parse_float=Decimal)
            validator = ImmunizationValidator()
            self.assertTrue(validator.validate(valid_json_data))


class TestImmunizationModelPostValidationRules(unittest.TestCase):
    """Test immunization post validation rules on the FHIR model"""

    def setUp(self):
        """Set up for each test. This runs before every test"""
        self.json_data = load_json_data_for_tests(
            "sample_covid_immunization_event.json"
        )
        self.validator = ImmunizationValidator()

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
            field_location=field_location,
        )

    def test_model_post_status(self):
        """
        Test that when status field is absent it is rejected (by FHIR validator) and when it is
        present the status property is set equal to it
        """
        valid_json_data = deepcopy(self.json_data)

        # Test that status property is set to the value of status in the JSON data, where it exists
        for valid_value in ["completed", "entered-in-error"]:
            valid_json_data = parse("status").update(valid_json_data, valid_value)
            self.validator.validate(valid_json_data)
            self.assertEqual(valid_value, self.validator.immunization.status)

        # This error is raised by the FHIR validator (status is a mandatory FHIR field)
        MandationTests.test_missing_mandatory_field_rejected(
            self,
            valid_json_data=valid_json_data,
            field_location="status",
            expected_bespoke_error_message="field required",
            expected_error_type="value_error.missing",
            is_mandatory_fhir=True,
        )

        # TODO: Add similar test to the not-done data, testing when status is not-done

    def test_model_post_patient_identifier_value(self):
        """
        Test that the JSON data is accepted whether or not it contains
        contained[?(@.resourceType=='Patient')].identifier[0].value
        """
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, "contained[?(@.resourceType=='Patient')].identifier[0].value"
        )

    def test_model_post_patient_name_given(self):
        """
        Test that the JSON data is rejected if it does not contain
        contained[?(@.resourceType=='Patient')].name[0].given
        """
        MandationTests.test_missing_mandatory_field_rejected(
            self, "contained[?(@.resourceType=='Patient')].name[0].given"
        )

    def test_model_post_patient_name_family(self):
        """
        Test that the JSON data is rejected if it does not contain
        contained[?(@.resourceType=='Patient')].name[0].family
        """
        MandationTests.test_missing_mandatory_field_rejected(
            self, "contained[?(@.resourceType=='Patient')].name[0].family"
        )

    def test_model_post_patient_birth_date(self):
        """
        Test that the JSON data is rejected if it does not contain
        contained[?(@.resourceType=='Patient')].birthDate
        """
        MandationTests.test_missing_mandatory_field_rejected(
            self, "contained[?(@.resourceType=='Patient')].birthDate"
        )

    def test_model_post_patient_gender(self):
        """
        Test that the JSON data is rejected if it does not contain
        contained[?(@.resourceType=='Patient')].gender
        """
        MandationTests.test_missing_mandatory_field_rejected(
            self, "contained[?(@.resourceType=='Patient')].gender"
        )

    def test_model_post_patient_address_postal_code(self):
        """
        Test that the JSON data is rejected if it does not contain
        contained[?(@.resourceType=='Patient')].address[0].postalCode
        """
        MandationTests.test_missing_mandatory_field_rejected(
            self, "contained[?(@.resourceType=='Patient')].address[0].postalCode"
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
            field_location,
            valid_json_data,
            expected_bespoke_error_message="Expect any of field value from this list "
            + "['occurrenceDateTime', 'occurrenceString'].",
            expected_error_type="value_error",
            is_mandatory_fhir=True,
        )

    def test_model_post_organization_identifier_value(self):
        """
        Test that the JSON data is accepted if it contains
        performer[?(@.actor.type=='Organization').identifier.value] and rejected if not
        """
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self, "performer[?(@.actor.type=='Organization')].actor.identifier.value"
        )

    def test_model_post_organization_display(self):
        """
        Test that the JSON data is accepted if it contains
        performer[?(@.actor.type=='Organization')].actor.display and rejected if not
        """
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self, "performer[?(@.actor.type=='Organization')].actor.display"
        )

    def test_model_post_identifer_value(self):
        """
        Test that the JSON data is accepted if it contains identifier[0].value and rejected if not
        """
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self, "identifier[0].value"
        )

    def test_model_post_identifer_system(self):
        """
        Test that the JSON data is accepted if it contains identifier[0].system and rejected if not
        """
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self,
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self, "identifier[0].system"
        )

    def test_model_post_practitioner_name_given(self):
        """
        Test that the JSON data is accepted if it does not contain
        contained[?(@.resourceType=='Practitioner')].name[0].given
        """
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, "contained[?(@.resourceType=='Practitioner')].name[0].given"
        )

    def test_model_post_practitioner_name_family(self):
        """
        Test that the JSON data is accepted if it does not contain
        contained[?(@.resourceType=='Practitioner')].name[0].family
        """
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, "contained[?(@.resourceType=='Practitioner')].name[0].family"
        )

    def test_model_post_practitioner_identifier_value(self):
        """
        Test that the JSON data is rejected if it does not contain
        contained[?(@.resourceType=='Practitioner')].identifier[0].value
        """
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, "contained[?(@.resourceType=='Practitioner')].identifier[0].value"
        )

    def test_model_post_practitioner_identifier_system(self):
        """
        Test that the JSON data is rejected if it does not contain
        contained[?(@.resourceType=='Practitioner')].identifier[0].system
        """
        field_location = (
            "contained[?(@.resourceType=='Practitioner')].identifier[0].system"
        )
        vaccination_procdeure_code_field_location = (
            "extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/"
            + "Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[?(@.system=="
            + "'http://snomed.info/sct')].code"
        )
        practitioner_identifier_value_field_location = (
            "contained[?(@.resourceType=='Practitioner')].identifier[0].value"
        )

        valid_covid_19_procedure_code = "1324681000000101"
        valid_flu_procedure_code = "mockFLUcode1"
        valid_hpv_procedure_code = "mockHPVcode1"
        valid_mmr_procedure_code = "mockMMRcode1"

        # Test COVID-19 cases where practitioner_identifier_value is present
        valid_covid_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_covid_19_procedure_code
        )

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_covid_json_data
        )

        # Test case: patient_identifier_system absent - reject
        MandationTests.test_missing_mandatory_field_rejected(
            self,
            field_location,
            valid_covid_json_data,
            expected_bespoke_error_message=f"{field_location} is mandatory when contained."
            + "[?(@.resourceType=='Practitioner')].identifier[0].system is present"
            + " and vaccination type is COVID-19",
        )

        # Test COVID-19 cases where practitioner_identifier_value is absent
        valid_covid_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_covid_19_procedure_code
        )
        valid_covid_json_data = parse(
            practitioner_identifier_value_field_location
        ).filter(lambda d: True, valid_covid_json_data)

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_covid_json_data
        )

        # Test case: patient_identifier_system absent - accept
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location, valid_covid_json_data
        )

        # Test FLU cases where practitioner_identifier_value is present
        valid_flu_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_flu_procedure_code
        )

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_flu_json_data
        )

        # Test case: patient_identifier_system absent - reject
        MandationTests.test_missing_mandatory_field_rejected(
            self,
            field_location,
            valid_flu_json_data,
            expected_bespoke_error_message=f"{field_location} is mandatory when contained."
            + "[?(@.resourceType=='Practitioner')].identifier[0].system is present"
            + " and vaccination type is FLU",
        )

        # Test FLU cases where practitioner_identifier_value is absent
        valid_flu_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_flu_procedure_code
        )
        valid_flu_json_data = parse(
            practitioner_identifier_value_field_location
        ).filter(lambda d: True, valid_flu_json_data)

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_flu_json_data
        )

        # Test case: patient_identifier_system absent - accept
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location, valid_flu_json_data
        )

        # Test HPV cases where practitioner_identifier_value is present
        valid_hpv_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_hpv_procedure_code
        )

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_hpv_json_data
        )

        # Test case: patient_identifier_system absent - reject
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location, valid_hpv_json_data
        )

        # Test HPV cases where practitioner_identifier_value is absent
        valid_hpv_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_hpv_procedure_code
        )
        valid_hpv_json_data = parse(
            practitioner_identifier_value_field_location
        ).filter(lambda d: True, valid_hpv_json_data)

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_hpv_json_data
        )

        # Test case: patient_identifier_system absent - accept
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location, valid_hpv_json_data
        )

        # Test MMR cases where practitioner_identifier_value is present
        valid_mmr_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_mmr_procedure_code
        )

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_mmr_json_data
        )

        # Test case: patient_identifier_system absent - reject
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location, valid_mmr_json_data
        )

        # Test MMR cases where practitioner_identifier_value is absent
        valid_mmr_json_data = parse(vaccination_procdeure_code_field_location).update(
            deepcopy(self.json_data), valid_mmr_procedure_code
        )
        valid_mmr_json_data = parse(
            practitioner_identifier_value_field_location
        ).filter(lambda d: True, valid_mmr_json_data)

        # Test case: patient_identifier_system present - accept
        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_mmr_json_data
        )

        # Test case: patient_identifier_system absent - accept
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location, valid_mmr_json_data
        )

    def test_model_post_perfomer_sds_job_role(self):
        """
        Test that the JSON data is accepted if it does not contain contained[?(@.resourceType==
        'QuestionnaireResponse')].item[?(@.linkId=='PerformerSDSJobRole')].answer[0].valueString"
        """
        field_location = (
            "contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='PerformerSDSJobRole')].answer[0].valueString"
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location
        )

    def test_model_post_recorded(self):
        """
        Test that the JSON data is accepted if it contains recorded and rejected if not
        """
        field_location = "recorded"

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            field_location,
            expected_bespoke_error_message=f"{field_location} is a mandatory field",
        )

    def test_model_post_primary_source(self):
        """
        Test that the JSON data is accepted if it contains primarySource and rejected if not
        """
        MandationTests.test_missing_mandatory_field_rejected(self, "primarySource")

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
            self, field_location, json_data_with_primary_source_true
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
            field_location,
            json_data_with_primary_source_false,
            expected_bespoke_error_message=f"{field_location} is mandatory when primarySource"
            + " is false",
            expected_error_type="MandatoryError",
        )

    def test_model_post_vaccination_procedure_display(self):
        """
        Test that the JSON data is accepted when vaccination_procedure_display is present or absent
        """
        field_location = (
            "extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/"
            + "Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[?(@.system=="
            + "'http://snomed.info/sct')].display"
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location
        )

    def test_model_post_vaccination_situation_code(self):
        """
        Test that the JSON data is accepted if it contains vaccination_situation_code
        and rejected if not

        NOTE: This test runs on the COVID data. Further tests for other cases are run on the
        not-done data.
        """
        field_location = (
            "extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/"
            + "Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[?(@.system=="
            + "'http://snomed.info/sct')].code"
        )

        MandationTests.test_mandation_for_mandatory_if_not_done_on_not_not_done_data(
            self, field_location
        )

    def test_model_post_vaccination_situation_display(self):
        """
        Test that the JSON data is accepted when vaccination_situation_display is present or absent
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = (
            "extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/"
            + "Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[?(@.system=="
            + "'http://snomed.info/sct')].display"
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, field_location
        )

    def test_model_post_status_reason_coding_code(self):
        """
        Test that the JSON data is accepted if it contains status_reason_coding_code
        and rejected if not

        NOTE: This test runs on the COVID data. Further tests for other cases are run on the
        not-done data.
        """
        MandationTests.test_mandation_for_mandatory_if_not_done_on_not_not_done_data(
            self, "statusReason.coding[?(@.system=='http://snomed.info/sct')].code"
        )

    def test_model_post_status_reason_coding_display(self):
        """
        Test that the JSON data is accepted when status_reason_coding_display is present or absent
        """
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, "statusReason.coding[?(@.system=='http://snomed.info/sct')].code"
        )

    # TODO: Complete this test
    def test_model_post_protocol_applied_dose_number_positive_int(self):
        """
        Test that the JSON data is accepted when protocol_applied_dose_number_positive_int
        is present or absent
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = "protocolApplied[0].doseNumberPositiveInt"

        # Test cases for COVID-19
        # COVID-19, status="completed", field present - accept
        # COVID-19, status="completed", field missing - reject
        # COVID-19, status="entered-in-error", field present - accept
        # COVID-19, status=entered-in-error", field missing - reject

        # Test cases for FLU
        # FLU, status="completed", field present - accept
        # FLU, status="completed", field missing - reject
        # FLU, status="entered-in-error", field present - accept
        # FLU, status=entered-in-error", field missing - reject

        # Test cases for HPV
        # HPV, status="completed", field present - accept
        # HPV, status="completed", field missing - accept
        # HPV, status="entered-in-error", field present - accept
        # HPV, status=entered-in-error", field missing - accept

        # Test cases for MMR
        # MMR, status="completed", field present - accept
        # MMR, status="completed", field missing - accept
        # MMR, status="entered-in-error", field present - accept
        # MMR, status=entered-in-error", field missing - accept

    # TODO: need to check for the valid values for not-done and the invalid values
    def test_model_post_vaccine_code_coding_code(self):
        """
        Test that the JSON data is accepted if it contains vaccine_code_coding_code
        and rejected if not
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = (
            "vaccineCode.coding[?(@.system=='http://snomed.info/sct')].code"
        )

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            self, valid_json_data
        )

        MandationTests.test_missing_mandatory_field_rejected(
            self,
            field_location,
            valid_json_data=valid_json_data,
            expected_error_type="MandatoryError",
        )

    def test_model_post_vaccine_code_coding_display(self):
        """
        Test that the JSON data is accepted when vaccine_code_coding_display is present or absent
        """
        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            self, "vaccineCode.coding[?(@.system=='http://snomed.info/sct')].display"
        )


class TestImmunizationModelPostValidationRulesForNotDone(unittest.TestCase):
    """Test immunization post validation rules on the FHIR model using the status="not-done" data"""

    def setUp(self):
        """Set up for each test. This runs before every test"""
        self.json_data = load_json_data_for_tests(
            "sample_immunization_not_done_event.json"
        )
        self.validator = ImmunizationValidator(add_post_validators=False)

    # TODO: Run this test on not-done data once need for vaccination_procedure_code confirmed
    # with imms team
    def test_model_post_vaccination_situation_code(self):
        """
        Test that the JSON data is accepted if it contains vaccination_situation_code
        and rejected if not

        NOTE: This test runs on the not-done data. Further tests for other cases are run on the
        COVID data.
        """
        valid_json_data = deepcopy(self.json_data)
        field_location = (
            "extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/"
            + "Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[?(@.system=="
            + "'http://snomed.info/sct')].code"
        )
        # # Test field is present when status is "not-done"
        # json_data_with_status_not_done = parse("status").update(
        #     deepcopy(valid_json_data), "not-done"
        # )

        # MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
        #     self, json_data_with_status_not_done
        # )

        # MandationTests.test_missing_mandatory_field_rejected(
        #     self,
        #     json_data_with_status_not_done,
        #     field_location,
        #     expected_error_message=f"{field_location} is mandatory when status is 'not-done'",
        #     expected_error_type="MandatoryError",
        # )

        # TODO: Add not-done tests for status_reason_coding_code

        # TODO: Add not-done tests for protcol_applied_dose_number_positive_int
        # (8 test cases - field present or missing for each of the 4 vaccine types)
