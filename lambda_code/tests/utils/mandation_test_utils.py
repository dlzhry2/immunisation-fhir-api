"""Mandation test utilities"""

import unittest
from copy import deepcopy
from typing import Literal
from pydantic import ValidationError
from jsonpath_ng.ext import parse
from models.utils.post_validation_utils import MandatoryError, NotApplicableError
from mappings import VaccineTypes


class MandationTests:
    """Test for presence of fields with different mandation levels"""

    @staticmethod
    def test_present_mandatory_or_required_or_optional_field_accepted(
        test_instance: unittest.TestCase,
        valid_json_data: dict = None,
    ):
        """
        Test that JSON data is accepted when a mandatory, required or optional field is present
        """
        # Prepare the json data
        if not valid_json_data:
            valid_json_data = deepcopy(test_instance.json_data)
        # Test that the valid data is accepted by the model
        test_instance.assertTrue(test_instance.validator.validate(valid_json_data))

    @staticmethod
    def test_missing_required_or_optional_or_not_applicable_field_accepted(
        test_instance: unittest.TestCase,
        field_location: str,
        valid_json_data: dict = None,
    ):
        """
        Test that JSON data which is missing a required,optional or not applicable field is accepted
        """
        # Prepare the json data
        if not valid_json_data:
            valid_json_data = deepcopy(test_instance.json_data)
        # Remove the relevant field
        valid_json_data = parse(field_location).filter(lambda d: True, valid_json_data)
        # Test that the valid data is accepted by the model
        test_instance.assertTrue(test_instance.validator.validate(valid_json_data))

    @staticmethod
    def test_missing_mandatory_field_rejected(
        test_instance: unittest.TestCase,
        field_location: str,
        valid_json_data: dict = None,
        expected_bespoke_error_message: str = None,
        expected_error_type: str = "value_error",
        is_mandatory_fhir: bool = False,
    ):
        """
        Test that json data which is missing a mandatory field is rejected by the model, with
        an appropriate validation error. Note that missing mandatory FHIR fields are rejected
        by the FHIR validator, whereas missing mandatory NHS fields are rejected by the custom
        validator.

        NOTE:
        TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
        this happens, the error message is suffixed with the type of error e.g. type_error or
        value_error. This is why the test checks for the type of error in the error message.
        """
        # Prepare the json data
        if not valid_json_data:
            valid_json_data = deepcopy(test_instance.json_data)
        from icecream import ic

        ic(valid_json_data)

        # Set the expected error message
        if expected_bespoke_error_message:
            expected_error_message = expected_bespoke_error_message
        else:
            expected_error_message = f"{field_location} is a mandatory field"

        # Create invalid json data by removing the relevant field
        invalid_json_data = parse(field_location).filter(
            lambda d: True, valid_json_data
        )

        if is_mandatory_fhir:
            # Test that correct error message is raised
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                (expected_bespoke_error_message + f" (type={expected_error_type})")
                in str(error.exception)
            )

        else:
            # Test that correct error message is raised
            with test_instance.assertRaises(MandatoryError) as error:
                test_instance.validator.validate(invalid_json_data)
            test_instance.assertEqual(expected_error_message, str(error.exception))

    @staticmethod
    def test_present_not_applicable_field_rejected(
        test_instance: unittest.TestCase,
        invalid_json_data: dict,
        field_location: str,
    ):
        """
        TODO: Test that JSON data containing a not applicable field is rejected.

        NOTE:
        TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
        this happens, the error message is suffixed with the type of error e.g. type_error or
        value_error. This is why the test checks for the type of error in the error message.
        """

        # Test that correct error message is raised
        with test_instance.assertRaises(NotApplicableError) as error:
            test_instance.validator.validate(invalid_json_data)
        test_instance.assertEqual(
            f"{field_location} must not be provided for this vaccine type",
            str(error.exception),
        )

    @staticmethod
    def test_mandation_for_mandatory_if_not_done_on_not_not_done_data(
        test_instance: unittest.TestCase,
        field_location: str,
    ):
        """
        Run all the test cases for status of "completed" or "entered-in-error" when the field
        is conditionally mandatory if status is "not-done"
        """

        # Test no errors are raised when status is "completed"
        json_data_with_status_entered_in_error = parse("status").update(
            deepcopy(test_instance.json_data), "completed"
        )

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            test_instance, json_data_with_status_entered_in_error
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            test_instance, field_location, json_data_with_status_entered_in_error
        )

        # Test no errors are raised when status is "entered-in-error"
        json_data_with_status_entered_in_error = parse("status").update(
            deepcopy(test_instance.json_data), "entered-in-error"
        )

        MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
            test_instance, json_data_with_status_entered_in_error
        )

        MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
            test_instance, field_location, json_data_with_status_entered_in_error
        )

    # @staticmethod
    # def test_conditional_mandation_for_field_present_or_missing(
    #     test_instance: unittest.TestCase,
    #     field_location_of_field_being_tested: str,
    #     field_location_of_field_mandation_is_dependent_on: str,
    #     vaccine_type: Literal["COVID-19", "FLU", "HPV", "MMR"],
    #     mandation_when_field_present: Literal["M", "CM", "R", "O", "N/A"],
    #     mandation_when_field_absent: Literal["M", "CM", "R", "O", "N/A"],
    #     expected_mandatory_error_message: str = None,
    #     expected_not_applicable_error_message: str = None,
    # ):
    #     """
    #     Something
    #     """

    #     vaccination_procedure_code_field_location = (
    #         "extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/"
    #         + "Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[?(@.system=="
    #         + "'http://snomed.info/sct')].code"
    #     )

    #     valid_procedure_codes_for_testing = {
    #         "COVID-19": "1324681000000101",
    #         "FLU": "mockFLUcode1",
    #         "HPV": "mockHPVcode1",
    #         "MMR": "mockMMRcode1",
    #     }

    #     # Obtain valid vaccination procedure code
    #     valid_procedure_code = valid_procedure_codes_for_testing[vaccine_type]

    #     # Test cases where practitioner_identifier_value is present
    #     valid_json_data = parse(vaccination_procedure_code_field_location).update(
    #         deepcopy(test_instance.json_data), valid_procedure_code
    #     )

    #     # Test case: patient_identifier_system present - accept
    #     MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
    #         test_instance, valid_json_data
    #     )

    #     # Test case: patient_identifier_system absent - reject
    #     MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
    #         test_instance, valid_json_data, field_location_of_field_being_tested
    #     )

    #     # Test MMR cases where practitioner_identifier_value is absent
    #     valid_json_data = parse(vaccination_procedure_code_field_location).update(
    #         deepcopy(test_instance.json_data), valid_procedure_code
    #     )
    #     valid_json_data = parse(field_location_of_field_being_tested).filter(
    #         lambda d: True, valid_json_data
    #     )

    #     # Test case: patient_identifier_system present - accept
    #     MandationTests.test_present_mandatory_or_required_or_optional_field_accepted(
    #         test_instance, valid_json_data
    #     )

    #     # Test case: patient_identifier_system absent - accept
    #     MandationTests.test_missing_required_or_optional_or_not_applicable_field_accepted(
    #         test_instance, valid_json_data, field_location_of_field_being_tested
    #     )
