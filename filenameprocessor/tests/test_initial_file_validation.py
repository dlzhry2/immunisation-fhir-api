"""Tests for file_key_validation functions"""

from unittest import TestCase
from unittest.mock import patch
from boto3 import client as boto3_client
from moto import mock_s3

from file_key_validation import is_valid_datetime, file_key_validation
from tests.utils_for_tests.values_for_tests import MOCK_ENVIRONMENT_DICT


@mock_s3
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestInitialFileValidation(TestCase):
    """Tests for file_key_validation functions"""

    def test_is_valid_datetime(self):
        "Tests that is_valid_datetime returns True for valid datetimes, and false otherwise"
        # Test case tuples are stuctured as (date_time_string, expected_result)
        test_cases = [
            ("20200101T12345600", True),  # Valid datetime string with timezone
            ("20200101T123456", True),  # Valid datetime string without timezone
            ("20200101T123456extracharacters", True),  # Valid datetime string with additional characters
            ("20201301T12345600", False),  # Invalid month
            ("20200100T12345600", False),  # Invalid day
            ("20200230T12345600", False),  # Invalid combination of month and day
            ("20200101T24345600", False),  # Invalid hours
            ("20200101T12605600", False),  # Invalid minutes
            ("20200101T12346000", False),  # Invalid seconds
            ("2020010112345600", False),  # Invalid missing the 'T'
            ("20200101T12345", False),  # Invalid string too short
        ]

        for date_time_string, expected_result in test_cases:
            with self.subTest():
                self.assertEqual(is_valid_datetime(date_time_string), expected_result)

    def test_file_key_validation(self):
        """Tests that file_key_validation returns True if all elements pass validation, and False otherwise"""
        bucket_name = "test_bucket"
        s3_client = boto3_client("s3", region_name="eu-west-2")
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        valid_file_key = "Flu_Vaccinations_v5_YGA_20200101T12345600.csv"
        test_file_content = "Test file content"

        # Test case tuples are structured as (file_key, expected_result)
        test_cases_for_success_scenarios = [
            # Valid flu file key (mixed case)
            (valid_file_key, ("FLU", "TPP")),
            # Valid covid19 file key (mixed case)
            (valid_file_key.replace("Flu", "Covid19"), ("COVID19", "TPP")),
            # Valid file key (all lowercase)
            (valid_file_key.lower(), ("FLU", "TPP")),
            # Valid file key (all uppercase)
            (valid_file_key.upper(), ("FLU", "TPP")),
        ]

        for file_key, expected_result in test_cases_for_success_scenarios:
            with self.subTest(f"SubTest for file key: {file_key}"):
                # Mock full permissions for the supplier (Note that YGA ODS code maps to the supplier 'TPP')
                s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=test_file_content)
                self.assertEqual(file_key_validation(file_key), expected_result)

        key_format_error_message = "Initial file validation failed: invalid file key format"
        invalid_file_key_error_message = "Initial file validation failed: invalid file key"
        test_cases_for_failure_scenarios = [
            # File key with no '.'
            (valid_file_key.replace(".", ""), key_format_error_message),
            # File key with additional '.'
            (valid_file_key[:2] + "." + valid_file_key[2:], key_format_error_message),
            # File key with additional '_'
            (valid_file_key[:2] + "_" + valid_file_key[2:], key_format_error_message),
            # File key with missing '_'
            (valid_file_key.replace("_", "", 1), key_format_error_message),
            # File key with missing '_'
            (valid_file_key.replace("_", ""), key_format_error_message),
            # File key with missing extension
            (valid_file_key.replace(".csv", ""), key_format_error_message),
            # File key with invalid vaccine type
            (valid_file_key.replace("Flu", "Flue"), invalid_file_key_error_message),
            # File key with missing vaccine type
            (valid_file_key.replace("Flu", ""), invalid_file_key_error_message),
            # File key with invalid vaccinations element
            (valid_file_key.replace("Vaccinations", "Vaccination"), invalid_file_key_error_message),
            # File key with missing vaccinations element
            (valid_file_key.replace("Vaccinations", ""), invalid_file_key_error_message),
            # File key with invalid version
            (valid_file_key.replace("v5", "v4"), invalid_file_key_error_message),
            # File key with missing version
            (valid_file_key.replace("v5", ""), invalid_file_key_error_message),
            # File key with invalid ODS code
            (valid_file_key.replace("YGA", "YGAM"), invalid_file_key_error_message),
            # File key with missing ODS code
            (valid_file_key.replace("YGA", "YGAM"), invalid_file_key_error_message),
            # File key with invalid timestamp
            (valid_file_key.replace("20200101T12345600", "20200132T12345600"), invalid_file_key_error_message),
            # File key with missing timestamp
            (valid_file_key.replace("20200101T12345600", ""), invalid_file_key_error_message),
            # File key with incorrect extension
            (valid_file_key.replace(".csv", ".dat"), invalid_file_key_error_message),
        ]

        for file_key, expected_result in test_cases_for_failure_scenarios:
            with self.subTest(f"SubTest for file key: {file_key}"):
                s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=test_file_content)
                with self.assertRaises(Exception) as context:
                    file_key_validation(file_key)
                self.assertEqual(str(context.exception), expected_result)
