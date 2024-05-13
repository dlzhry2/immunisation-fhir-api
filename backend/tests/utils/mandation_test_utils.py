"""Mandation test utilities"""

import unittest
from copy import deepcopy

from jsonpath_ng.ext import parse
from mappings import (
    VaccineTypes,
    Mandation,
    vaccine_type_mappings,
)
from models.utils.post_validation_utils import MandatoryError, NotApplicableError
from pydantic import ValidationError


class MandationTests:
    """Test for presence of fields with different mandation levels"""

    @staticmethod
    def prepare_json_data(test_instance: unittest.TestCase, json_data: dict = None) -> dict:
        """Returns json_data if given json_data, otherwise returns the valid covid json data as a default"""
        return json_data if json_data else test_instance.valid_json_data[VaccineTypes.covid_19]

    @staticmethod
    def update_target_disease(
        test_instance: unittest.TestCase,
        vaccine_type: VaccineTypes,
        valid_json_data: dict = None,
    ):
        """Update the target_disease in the data to match the vaccine type"""

        valid_json_data = MandationTests.prepare_json_data(test_instance, valid_json_data)

        # Set the target disease field value based on vaccine type
        target_disease_codes = next(x[0] for x in vaccine_type_mappings if x[1] == vaccine_type)
        target_disease = []
        for code in target_disease_codes:
            target_disease.append({"coding": [{"system": "http://snomed.info/sct", "code": code, "display": "Dummy"}]})

        return parse("protocolApplied[0].targetDisease").update(deepcopy(valid_json_data), target_disease)

    @staticmethod
    def test_present_field_accepted(
        test_instance: unittest.TestCase,
        valid_json_data: dict = None,
    ):
        """Test that JSON data is accepted when a field is present"""
        valid_json_data = MandationTests.prepare_json_data(test_instance, valid_json_data)
        test_instance.assertTrue(test_instance.validator.validate(valid_json_data))

    @staticmethod
    def test_missing_field_accepted(
        test_instance: unittest.TestCase,
        field_location: str,
        valid_json_data: dict = None,
        field_to_remove: str = None,
    ):
        """
        Test that JSON data which is missing a required,optional or not applicable field is accepted

        NOTE: By default the field_location being tested is removed. If required, a parent
        field can be given to the optional field_to_remove argument instead.
        """
        # Prepare the data
        valid_json_data = MandationTests.prepare_json_data(test_instance, valid_json_data)
        field_to_remove = field_to_remove if field_to_remove else field_location
        valid_json_data = parse(field_to_remove).filter(lambda d: True, valid_json_data)

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
        field_to_remove: str = None,
    ):
        """
        Test that json data which is missing a mandatory field is rejected by the model, with
        an appropriate validation error. Note that missing mandatory FHIR fields are rejected
        by the FHIR validator, whereas missing mandatory NHS fields are rejected by the custom
        validator.

        NOTE: By default the field_location being tested is removed. If required, a parent
        field can be given to the optional field_to_remove argument instead.

        NOTE:
        TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
        this happens, the error message is suffixed with the type of error e.g. type_error or
        value_error. This is why the test checks for the type of error in the error message.
        """
        # Prepare the json data
        valid_json_data = MandationTests.prepare_json_data(test_instance, valid_json_data)
        field_to_remove = field_to_remove if field_to_remove else field_location
        invalid_json_data = parse(field_to_remove).filter(lambda d: True, valid_json_data)

        # Set the expected error message
        if expected_bespoke_error_message:
            expected_error_message = expected_bespoke_error_message
        else:
            expected_error_message = f"{field_location} is a mandatory field"

        if is_mandatory_fhir:
            # Test that correct error message is raised
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)
            test_instance.assertTrue(
                (expected_bespoke_error_message + f" (type={expected_error_type})") in str(error.exception)
            )

        else:
            # Test that correct error message is raised
            with test_instance.assertRaises(ValueError) as error:
                test_instance.validator.validate(invalid_json_data)
            test_instance.assertEqual(expected_error_message, str(error.exception))

    @staticmethod
    def test_present_not_applicable_field_rejected(
        test_instance: unittest.TestCase,
        field_location: str,
        invalid_json_data: dict = None,
        expected_bespoke_error_message: str = None,
        expected_error_type: str = "value_error",
        is_mandatory_fhir: bool = False,
    ):
        """
        NOTE:
        TypeErrors and ValueErrors are caught and converted to ValidationErrors by pydantic. When
        this happens, the error message is suffixed with the type of error e.g. type_error or
        value_error. This is why the test checks for the type of error in the error message.
        """
        invalid_json_data = MandationTests.prepare_json_data(test_instance, invalid_json_data)

         # Set the expected error message
        if expected_bespoke_error_message:
            expected_error_message = expected_bespoke_error_message
        else:
            expected_error_message = f"{field_location} must not be provided for this vaccine type"

        if is_mandatory_fhir:
            # Test that correct error message is raised
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)
            test_instance.assertTrue(
                (expected_bespoke_error_message + f" (type={expected_error_type})") in str(error.exception)
            )    

        # Test that correct error message is raised
        else:
            # Test that correct error message is raised
            with test_instance.assertRaises(NotApplicableError) as error:
                test_instance.validator.validate(invalid_json_data)
            eoor = error
            print(eoor)    
            test_instance.assertEqual(expected_error_message, str(error.exception))

        

    @staticmethod
    def test_mandation_rule_met(
        test_instance: unittest.TestCase,
        field_location: str,
        mandation: str,
        valid_json_data: dict,
        expected_bespoke_error_message: str = None,
        expected_error_type: str = "value_error",
        field_to_remove: str = None,
    ):
        """
        Test that the mandation rule is met (i.e. data is rejected or accepted as appropriate
        when field is present or absent)
        """
        if mandation == Mandation.mandatory:
            # Accept field present
            MandationTests.test_present_field_accepted(test_instance, valid_json_data)
            # Reject field absent
            MandationTests.test_missing_mandatory_field_rejected(
                test_instance,
                field_location,
                valid_json_data,
                expected_bespoke_error_message,
                expected_error_type,
                field_to_remove=field_to_remove,
            )

        if mandation == Mandation.required or mandation == Mandation.optional:
            # Accept field present
            MandationTests.test_present_field_accepted(test_instance, valid_json_data)
            # Accept field absent
            MandationTests.test_missing_field_accepted(
                test_instance, field_location, valid_json_data, field_to_remove=field_to_remove
            )

        # # TODO: Handle not applicable instance
        # if mandation == Mandation.not_applicable:
        #     # Reject field present
        #     MandationTests.test_present_not_applicable_field_rejected(test_instance, valid_json_data)
        #     # Accept field absent
        #     MandationTests.test_missing_field_accepted(
        #         test_instance, field_location, valid_json_data, field_to_remove=field_to_remove
        #     )

    @staticmethod
    def test_mandation_for_status_dependent_fields(
        test_instance: unittest.TestCase,
        field_location: str,
        vaccine_type: VaccineTypes,
        mandation_when_status_completed: Mandation,
        mandation_when_status_entered_in_error: Mandation,
        mandation_when_status_not_done: Mandation,
        expected_bespoke_error_message: str = None,
        expected_error_type: str = "value_error",
        field_to_remove: str = None,
    ):
        """
        Run all the test cases for the three different statuses,
        when mandation is dependent on status
        """
        # Set the vaccination procedure code based on vaccine type
        if vaccine_type == VaccineTypes.covid_19:
            valid_json_data = test_instance.covid_json_data
            base_not_done_json_data = test_instance.not_done_covid_json_data
        elif vaccine_type == VaccineTypes.flu:
            valid_json_data = test_instance.flu_json_data
            base_not_done_json_data = test_instance.not_done_json_data
        elif vaccine_type == VaccineTypes.hpv:
            valid_json_data = test_instance.hpv_json_data
            base_not_done_json_data = test_instance.not_done_json_data
        elif vaccine_type == VaccineTypes.mmr:
            valid_json_data = test_instance.mmr_json_data
            base_not_done_json_data = test_instance.not_done_mmr_json_data

        valid_json_data = MandationTests.update_target_disease(
            test_instance, vaccine_type, valid_json_data=deepcopy(valid_json_data)
        )

        # Test case where status is "completed"
        json_data_with_status_completed = parse("status").update(deepcopy(valid_json_data), "completed")

        MandationTests.test_mandation_rule_met(
            test_instance,
            field_location,
            mandation_when_status_completed,
            json_data_with_status_completed,
            expected_bespoke_error_message,
            expected_error_type,
            field_to_remove=field_to_remove,
        )

        # Test case where status is "entered-in-error"
        json_data_with_status_entered_in_error = parse("status").update(deepcopy(valid_json_data), "entered-in-error")

        MandationTests.test_mandation_rule_met(
            test_instance,
            field_location,
            mandation_when_status_entered_in_error,
            json_data_with_status_entered_in_error,
            expected_bespoke_error_message,
            expected_error_type,
            field_to_remove=field_to_remove,
        )

        # Test case where status is "not-done"
        base_not_done_json_data = deepcopy(base_not_done_json_data)

        json_data_with_status_not_done = MandationTests.update_target_disease(
            test_instance, vaccine_type, base_not_done_json_data
        )

        MandationTests.test_mandation_rule_met(
            test_instance,
            field_location,
            mandation_when_status_not_done,
            json_data_with_status_not_done,
            expected_bespoke_error_message,
            expected_error_type,
            field_to_remove=field_to_remove,
        )

    @staticmethod
    def test_mandation_for_interdependent_fields(
        test_instance: unittest.TestCase,
        dependent_field_location: str,
        dependent_on_field_location: str,
        vaccine_type: VaccineTypes,
        mandation_when_dependent_on_field_present: Mandation,
        mandation_when_dependent_on_field_absent: Mandation,
        expected_bespoke_error_message: str = None,
        expected_error_type: str = "value_error",
        valid_json_data: dict = None,
    ):
        """
        Run all the test cases for status of "completed" or "entered-in-error" when the field
        is conditionally mandatory if status is "not-done"
        """

        # Set the vaccination procedure code based on vaccine type
        valid_json_data = MandationTests.update_target_disease(
            test_instance, vaccine_type, valid_json_data=valid_json_data
        )

        # Test cases where depent_on_field is present
        MandationTests.test_mandation_rule_met(
            test_instance,
            field_location=dependent_field_location,
            mandation=mandation_when_dependent_on_field_present,
            valid_json_data=deepcopy(valid_json_data),
            expected_bespoke_error_message=expected_bespoke_error_message,
            expected_error_type=expected_error_type,
        )

        # Test case where depent_on_field is absent
        valid_json_data = parse(dependent_on_field_location).filter(lambda d: True, valid_json_data)

        MandationTests.test_mandation_rule_met(
            test_instance,
            field_location=dependent_field_location,
            mandation=mandation_when_dependent_on_field_absent,
            valid_json_data=deepcopy(valid_json_data),
            expected_bespoke_error_message=expected_bespoke_error_message,
            expected_error_type=expected_error_type,
        )
