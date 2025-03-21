"""Tests for the utils_for_recordprocessor module"""

import unittest
from unittest.mock import patch
from io import StringIO
import csv
import boto3
from moto import mock_s3
from tests.utils_for_recordprocessor_tests.utils_for_recordprocessor_tests import GenericSetUp, GenericTearDown
from tests.utils_for_recordprocessor_tests.values_for_recordprocessor_tests import (
    MockFileDetails,
    ValidMockFileContent,
    REGION_NAME,
)
from tests.utils_for_recordprocessor_tests.mock_environment_variables import MOCK_ENVIRONMENT_DICT, BucketNames

with patch("os.environ", MOCK_ENVIRONMENT_DICT):
    from utils_for_recordprocessor import get_environment, get_csv_content_dict_reader, create_diagnostics_dictionary, extract_content


s3_client = boto3.client("s3", region_name=REGION_NAME)
test_file = MockFileDetails.rsv_emis


@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
@mock_s3
class TestUtilsForRecordprocessor(unittest.TestCase):
    """Tests for utils_for_recordprocessor"""

    def setUp(self) -> None:
        GenericSetUp(s3_client)

    def tearDown(self) -> None:
        GenericTearDown(s3_client)

    @staticmethod
    def upload_source_file(file_key, file_content):
        """
        Uploads a test file with the test_file.file_key (Flu EMIS file) the given file content to the source bucket
        """
        s3_client.put_object(Bucket=BucketNames.SOURCE, Key=file_key, Body=file_content)

    def test_get_csv_content_dict_reader(self):
        """Tests that get_csv_content_dict_reader returns the correct csv data"""
        self.upload_source_file(test_file.file_key, ValidMockFileContent.with_new_and_update)
        expected_output = csv.DictReader(StringIO(ValidMockFileContent.with_new_and_update), delimiter="|")
        result, csv_data = get_csv_content_dict_reader(test_file.file_key)
        self.assertEqual(list(result), list(expected_output))
        self.assertEqual(csv_data, ValidMockFileContent.with_new_and_update)

    def test_get_environment(self):
        """Tests that get_environment returns the correct environment"""
        # Each test case tuple has the structure (environment, expected_result)
        test_cases = (
            ("internal-dev", "internal-dev"),
            ("int", "int"),
            ("ref", "ref"),
            ("sandbox", "sandbox"),
            ("prod", "prod"),
            ("pr-22", "internal-dev"),
        )

        for environment, expected_result in test_cases:
            with self.subTest(f"SubTest for environment: {environment}"):
                with patch.dict("os.environ", {"ENVIRONMENT": environment}):
                    self.assertEqual(get_environment(), expected_result)

    def test_create_diagnostics_dictionary(self):
        """Tests that create_diagnostics_dictionary returns the correct diagnostics dictionary"""
        self.assertEqual(
            create_diagnostics_dictionary("test error type", 400, "test error message"),
            {
                "error_type": "test error type",
                "statusCode": 400,
                "error_message": "test error message",
            },
        )

    def test_extract_content_valid_input(self):
        dat_file_content = (
            "----------------------------1234567890\n"
            "Content-Disposition: form-data; name=\"file\"; filename=\"COVID19_Vaccinations_v5_YGM41_20250312T113455981.csv\"\n"
            "Content-Type: text/csv\n\n"
            "NHS_NUMBER|PERSON_FORENAME|PERSON_SURNAME|PERSON_DOB|PERSON_GENDER_CODE|PERSON_POSTCODE\n"
            "----------------------------1234567890\n")
        expected_content = "NHS_NUMBER|PERSON_FORENAME|PERSON_SURNAME|PERSON_DOB|PERSON_GENDER_CODE|PERSON_POSTCODE"
        result = extract_content(dat_file_content)
        self.assertEqual(result, expected_content)


if __name__ == "__main__":
    unittest.main()
