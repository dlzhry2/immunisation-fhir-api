"""Mandation test utilities"""

import unittest
from pydantic import ValidationError
from jsonpath_ng.ext import parse
from models.utils.post_validation_utils import MandatoryError, NotApplicableError


class MandationTests:
    """Test for presence of fields with different mandation levels"""

    @staticmethod
    def test_present_field_accepted(
        test_instance: unittest.TestCase,
        valid_json_data: dict,
    ):
        """
        Test that JSON data is accepted when a field is present
        """
        # Test that the valid data is accepted by the model
        test_instance.assertTrue(test_instance.validator.validate(valid_json_data))

    @staticmethod
    def test_missing_field_accepted(
        test_instance: unittest.TestCase,
        valid_json_data: dict,
        field_location: str,
    ):
        """
        Test that JSON data which is missing a field is accepted
        """
        # Remove the relevant field
        valid_json_data = parse(field_location).filter(lambda d: True, valid_json_data)
        # Test that the valid data is accepted by the model
        test_instance.assertTrue(test_instance.validator.validate(valid_json_data))

    @staticmethod
    def test_missing_mandatory_field_rejected(
        test_instance: unittest.TestCase,
        valid_json_data: dict,
        field_location: str,
        expected_error_message: str,
        expected_error_type: str,
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
        # Create invalid json data by removing the relevant field
        invalid_json_data = parse(field_location).filter(
            lambda d: True, valid_json_data
        )

        if is_mandatory_fhir:
            # Test that correct error message is raised
            with test_instance.assertRaises(ValidationError) as error:
                test_instance.validator.validate(invalid_json_data)

            test_instance.assertTrue(
                (expected_error_message + f" (type={expected_error_type})")
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
