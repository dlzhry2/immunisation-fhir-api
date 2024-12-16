import unittest
from unittest.mock import patch
import boto3
from moto import mock_s3
from batch_processing import validate_content_headers, validate_action_flag_permissions
from utils_for_recordprocessor import convert_string_to_dict_reader
from tests.utils_for_recordprocessor_tests.values_for_recordprocessor_tests import (
    MOCK_ENVIRONMENT_DICT,
    MockFileDetails,
    ValidMockFileContent,
    BucketNames,
    REGION_NAME,
)

s3_client = boto3.client("s3", region_name=REGION_NAME)

test_file = MockFileDetails.rsv_emis


@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
@mock_s3
class TestProcessLambdaFunction(unittest.TestCase):

    def setUp(self) -> None:
        for bucket_name in [BucketNames.SOURCE, BucketNames.DESTINATION]:
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": REGION_NAME})

    def tearDown(self) -> None:
        for bucket_name in [BucketNames.SOURCE, BucketNames.DESTINATION]:
            for obj in s3_client.list_objects_v2(Bucket=bucket_name).get("Contents", []):
                s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
            s3_client.delete_bucket(Bucket=bucket_name)

    @staticmethod
    def upload_source_file(file_key, file_content):
        """
        Uploads a test file with the test_file.file_key (Flu EMIS file) the given file content to the source bucket
        """
        s3_client.put_object(Bucket=BucketNames.SOURCE, Key=file_key, Body=file_content)

    def test_validate_content_headers(self):
        "Tests that validate_content_headers returns True for an exact header match and False otherwise"
        # Test case tuples are stuctured as (file_content, expected_result)
        test_cases = [
            (ValidMockFileContent.with_new_and_update, True),  # Valid file content
            (ValidMockFileContent.with_new_and_update.replace("SITE_CODE", "SITE_COVE"), False),  # Misspelled header
            (ValidMockFileContent.with_new_and_update.replace("SITE_CODE|", ""), False),  # Missing header
            (
                ValidMockFileContent.with_new_and_update.replace("PERSON_DOB|", "PERSON_DOB|EXTRA_HEADER|"),
                False,
            ),  # Extra header
        ]

        for file_content, expected_result in test_cases:
            with self.subTest():
                # validate_content_headers takes a csv dict reader as it's input
                test_data = convert_string_to_dict_reader(file_content)
                self.assertEqual(validate_content_headers(test_data), expected_result)

    def test_validate_action_flag_permissions(self):
        """
        Tests that validate_action_flag_permissions returns True if supplier has permissions to perform at least one
        of the requested CRUD operations for the given vaccine type, and False otherwise
        """
        # Set up test file content. Note that ValidFileContent has action flags in lower case
        valid_file_content = ValidMockFileContent.with_new_and_update
        valid_content_new_and_update_lowercase = valid_file_content
        valid_content_new_and_update_uppercase = valid_file_content.replace("new", "NEW").replace("update", "UPDATE")
        valid_content_new_and_update_mixedcase = valid_file_content.replace("new", "New").replace("update", "uPdAte")
        valid_content_new_and_delete_lowercase = valid_file_content.replace("update", "delete")
        valid_content_update_and_delete_lowercase = valid_file_content.replace("new", "delete").replace(
            "update", "UPDATE"
        )

        # Test case tuples are stuctured as (vaccine_type, vaccine_permissions, file_content, expected_result)
        test_cases = [
            # FLU, full permissions, lowercase action flags
            ("FLU", ["FLU_FULL"], valid_content_new_and_update_lowercase, True),
            # FLU, partial permissions, uppercase action flags
            ("FLU", ["FLU_CREATE"], valid_content_new_and_update_uppercase, True),
            # FLU, full permissions, mixed case action flags
            ("FLU", ["FLU_FULL"], valid_content_new_and_update_mixedcase, True),
            # FLU, partial permissions (create)
            ("FLU", ["FLU_DELETE", "FLU_CREATE"], valid_content_new_and_update_lowercase, True),
            # FLU, partial permissions (update)
            ("FLU", ["FLU_UPDATE"], valid_content_new_and_update_lowercase, True),
            # FLU, partial permissions (delete)
            ("FLU", ["FLU_DELETE"], valid_content_new_and_delete_lowercase, True),
            # FLU, no permissions
            ("FLU", ["FLU_UPDATE", "COVID19_FULL"], valid_content_new_and_delete_lowercase, False),
            # COVID19, full permissions
            ("COVID19", ["COVID19_FULL"], valid_content_new_and_delete_lowercase, True),
            # COVID19, partial permissions
            ("COVID19", ["COVID19_UPDATE"], valid_content_update_and_delete_lowercase, True),
            # COVID19, no permissions
            ("COVID19", ["FLU_CREATE", "FLU_UPDATE"], valid_content_update_and_delete_lowercase, False),
            # RSV, full permissions
            ("RSV", ["RSV_FULL"], valid_content_new_and_delete_lowercase, True),
            # RSV, partial permissions
            ("RSV", ["RSV_UPDATE"], valid_content_update_and_delete_lowercase, True),
            # RSV, no permissions
            ("RSV", ["FLU_CREATE", "FLU_UPDATE"], valid_content_update_and_delete_lowercase, False),
            # RSV, full permissions, mixed case action flags
            ("RSV", ["RSV_FULL"], valid_content_new_and_update_mixedcase, True),
        ]

        for vaccine_type, vaccine_permissions, file_content, expected_result in test_cases:
            with self.subTest():
                # validate_action_flag_permissions takes a csv dict reader as one of it's args
                self.assertEqual(
                    validate_action_flag_permissions("TEST_SUPPLIER", vaccine_type, vaccine_permissions, file_content),
                    expected_result,
                )


if __name__ == "__main__":
    unittest.main()
