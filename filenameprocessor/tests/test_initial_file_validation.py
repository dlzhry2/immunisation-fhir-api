"""Tests for initial_file_validation functions"""

from unittest import TestCase
from unittest.mock import patch
from boto3 import client as boto3_client
from moto import mock_s3

from initial_file_validation import is_valid_datetime, initial_file_validation
from tests.utils_for_tests.values_for_tests import MOCK_ENVIRONMENT_DICT, VALID_FILE_CONTENT


@mock_s3
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestInitialFileValidation(TestCase):
    """Tests for initial_file_validation functions"""

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

    def test_initial_file_validation(self):
        """Tests that initial_file_validation returns True if all elements pass validation, and False otherwise"""
        bucket_name = "test_bucket"
        s3_client = boto3_client("s3", region_name="eu-west-2")
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        valid_file_key = "Flu_Vaccinations_v5_YGA_20200101T12345600.csv"
        valid_file_content = VALID_FILE_CONTENT

        # Test case tuples are structured as (file_key, file_content, vaccine_type, supplier))
        test_cases_for_full_permissions = [
            # Valid flu file key (mixed case)
            (valid_file_key, valid_file_content, "FLU", "TPP"),
            # Valid covid19 file key (mixed case)
            (valid_file_key.replace("Flu", "Covid19"), valid_file_content, "COVID19", "TPP"),
            # Valid file key (all lowercase)
            (valid_file_key.lower(), valid_file_content, "FLU", "TPP"),
            # Valid file key (all uppercase)
            (valid_file_key.upper(), valid_file_content, "FLU", "TPP"),
        ]

        for file_key, file_content, vaccine_type, supplier in test_cases_for_full_permissions:
            with self.subTest(f"SubTest for file key: {file_key}"):
                # Mock full permissions for the supplier (Note that YGA ODS code maps to the supplier 'TPP')
                s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_content)
                self.assertEqual(initial_file_validation(file_key), (vaccine_type, supplier))

        key_format_error_message = "Initial file validation failed: invalid file key format"
        invalid_file_key_error_message = "Initial file validation failed: invalid file key"
        # TODO: Handle permissions

        test_cases_for_full_permissions = [
            # File key with no '.'
            (valid_file_key.replace(".", ""), valid_file_content, key_format_error_message),
            # File key with additional '.'
            (valid_file_key[:2] + "." + valid_file_key[2:], valid_file_content, key_format_error_message),
            # File key with additional '_'
            (valid_file_key[:2] + "_" + valid_file_key[2:], valid_file_content, key_format_error_message),
            # File key with missing '_'
            (valid_file_key.replace("_", "", 1), valid_file_content, key_format_error_message),
            # File key with missing '_'
            (valid_file_key.replace("_", ""), valid_file_content, key_format_error_message),
            # File key with missing extension
            (valid_file_key.replace(".csv", ""), valid_file_content, key_format_error_message),
            # File key with invalid vaccine type
            (valid_file_key.replace("Flu", "Flue"), valid_file_content, invalid_file_key_error_message),
            # File key with missing vaccine type
            (valid_file_key.replace("Flu", ""), valid_file_content, invalid_file_key_error_message),
            # File key with invalid vaccinations element
            (valid_file_key.replace("Vaccinations", "Vaccination"), valid_file_content, invalid_file_key_error_message),
            # File key with missing vaccinations element
            (valid_file_key.replace("Vaccinations", ""), valid_file_content, invalid_file_key_error_message),
            # File key with invalid version
            (valid_file_key.replace("v5", "v4"), valid_file_content, invalid_file_key_error_message),
            # File key with missing version
            (valid_file_key.replace("v5", ""), valid_file_content, invalid_file_key_error_message),
            # File key with invalid ODS code
            (valid_file_key.replace("YGA", "YGAM"), valid_file_content, invalid_file_key_error_message),
            # File key with missing ODS code
            (valid_file_key.replace("YGA", "YGAM"), valid_file_content, invalid_file_key_error_message),
            # File key with invalid timestamp
            (
                valid_file_key.replace("20200101T12345600", "20200132T12345600"),
                valid_file_content,
                invalid_file_key_error_message,
            ),
            # File key with missing timestamp
            (valid_file_key.replace("20200101T12345600", ""), valid_file_content, invalid_file_key_error_message),
            # File key with incorrect extension
            (valid_file_key.replace(".csv", ".dat"), valid_file_content, invalid_file_key_error_message),
        ]

        for file_key, file_content, expected_result in test_cases_for_full_permissions:
            with self.subTest(f"SubTest for file key: {file_key}"):
                # Mock full permissions for the supplier (Note that YGA ODS code maps to the supplier 'TPP')
                s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_content)
                with self.assertRaises(Exception) as context:
                    initial_file_validation(file_key)
                self.assertEqual(str(context.exception), expected_result)

        # # Partial permissions test cases
        # with self.subTest("SubTest for valid file key with partial permissions"):
        #     with patch(
        #         "initial_file_validation.get_permissions_config_json_from_cache",
        #         return_value={"all_permissions": {"TPP": ["FLU_CREATE"]}},
        #     ):
        #         s3_client.put_object(Bucket=bucket_name, Key=valid_file_key, Body=valid_file_content)
        #         self.assertEqual(initial_file_validation(valid_file_key), ("FLU", "TPP"))

        # with self.subTest("SubTest for invalid file key with partial permissions"):
        #     file_key_without_permissions = valid_file_key.replace("Flu", "Covid19")
        #     with patch(
        #         "initial_file_validation.get_permissions_config_json_from_cache",
        #         return_value={"all_permissions": {"TPP": ["FLU_CREATE"]}},
        #     ):
        #         s3_client.put_object(Bucket=bucket_name, Key=file_key_without_permissions, Body=valid_file_content)
        #         with self.assertRaises(Exception) as context:
        #             initial_file_validation(file_key_without_permissions)
        #         self.assertEqual(
        #             str(context.exception), "Initial file validation failed: TPP does not have permissions for COVID19"
        #         )
