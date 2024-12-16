import unittest
from unittest.mock import patch, MagicMock
import json
import boto3
from moto import mock_s3
from batch_processing import main, process_csv_to_fhir
from tests.utils_for_recordprocessor_tests.values_for_recordprocessor_tests import (
    MOCK_ENVIRONMENT_DICT,
    MockFileDetails,
    ValidMockFileContent,
    BucketNames,
    MockFieldDictionaries,
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

    def test_process_csv_to_fhir_full_permissions(self):
        self.upload_source_file(
            file_key=test_file.file_key, file_content=ValidMockFileContent.with_new_and_update_and_delete
        )

        with patch("batch_processing.send_to_kinesis") as mock_send_to_kinesis:
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        self.assertEqual(mock_send_to_kinesis.call_count, 3)

    def test_process_csv_to_fhir_partial_permissions(self):
        self.upload_source_file(
            file_key=test_file.file_key, file_content=ValidMockFileContent.with_new_and_update_and_delete
        )

        with patch("batch_processing.send_to_kinesis") as mock_send_to_kinesis:
            process_csv_to_fhir(test_file.event_create_permissions_only_dict)

        self.assertEqual(mock_send_to_kinesis.call_count, 3)

    def test_process_csv_to_fhir_no_permissions(self):
        self.upload_source_file(
            file_key=test_file.file_key, file_content=ValidMockFileContent.with_new_and_update_and_delete
        )

        with patch("batch_processing.send_to_kinesis") as mock_send_to_kinesis:
            process_csv_to_fhir(test_file.event_create_permissions_only_dict)

        self.assertEqual(mock_send_to_kinesis.call_count, 3)

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir(self, mock_send_to_kinesis):
        self.upload_source_file(file_key=test_file.file_key, file_content=ValidMockFileContent.with_new_and_update)

        with patch("batch_processing.get_operation_permissions", return_value={"CREATE", "UPDATE", "DELETE"}):
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        mock_send_to_kinesis.assert_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_(self, mock_send_to_kinesis):
        s3_client.put_object(Bucket=BucketNames.SOURCE, Key=test_file.file_key, Body=ValidMockFileContent.with_delete)

        process_csv_to_fhir(test_file.event_delete_permissions_only_dict)

        mock_send_to_kinesis.assert_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_positive_string_provided(self, mock_send_to_kinesis):
        s3_client.put_object(
            Bucket=BucketNames.SOURCE, Key=test_file.file_key, Body=ValidMockFileContent.with_new_and_update
        )

        with patch("batch_processing.get_operation_permissions", return_value={"CREATE", "UPDATE", "DELETE"}):
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        mock_send_to_kinesis.assert_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_only_mandatory(self, mock_send_to_kinesis):
        s3_client.put_object(
            Bucket=BucketNames.SOURCE, Key=test_file.file_key, Body=ValidMockFileContent.with_new_and_update
        )

        with patch("batch_processing.get_operation_permissions", return_value={"CREATE", "UPDATE", "DELETE"}):
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        mock_send_to_kinesis.assert_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_positive_string_not_provided(self, mock_send_to_kinesis):
        s3_client.put_object(
            Bucket=BucketNames.SOURCE, Key=test_file.file_key, Body=ValidMockFileContent.with_new_and_update
        )

        with patch("batch_processing.get_operation_permissions", return_value={"CREATE", "UPDATE", "DELETE"}):
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        mock_send_to_kinesis.assert_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_paramter_missing(self, mock_send_to_kinesis):
        s3_client.put_object(
            Bucket=BucketNames.SOURCE,
            Key=test_file.file_key,
            Body=ValidMockFileContent.with_new_and_update.replace("new", ""),
        )

        with patch("process_row.convert_to_fhir_imms_resource", return_value=({}, True)), patch(
            "batch_processing.get_operation_permissions", return_value={"CREATE", "UPDATE", "DELETE"}
        ):
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        mock_send_to_kinesis.assert_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_invalid_headers(self, mock_send_to_kinesis):
        self.upload_source_file(
            file_key=test_file.file_key,
            file_content=ValidMockFileContent.with_new_and_update.replace("NHS_NUMBER", "NHS_NUMBERS"),
        )

        process_csv_to_fhir(test_file.event_full_permissions_dict)
        mock_send_to_kinesis.assert_not_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_wrong_file_invalid_action_flag_permissions(self, mock_send_to_kinesis):
        s3_client.put_object(
            Bucket=BucketNames.SOURCE, Key=test_file.file_key, Body=ValidMockFileContent.with_new_and_update
        )

        process_csv_to_fhir(test_file.event_delete_permissions_only_dict)

        mock_send_to_kinesis.assert_not_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_successful(self, mock_send_to_kinesis):
        s3_client.put_object(Bucket=BucketNames.SOURCE, Key=test_file.file_key, Body=ValidMockFileContent.with_update)

        with patch("batch_processing.get_operation_permissions", return_value={"CREATE", "UPDATE", "DELETE"}):
            mock_csv_reader_instance = MagicMock()
            mock_csv_reader_instance.__iter__.return_value = iter(MockFieldDictionaries.all_fields)
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        mock_send_to_kinesis.assert_called()

    @patch("batch_processing.send_to_kinesis")
    def test_process_csv_to_fhir_incorrect_permissions(self, mock_send_to_kinesis):
        s3_client.put_object(Bucket=BucketNames.SOURCE, Key=test_file.file_key, Body=ValidMockFileContent.with_update)

        with patch("batch_processing.get_operation_permissions", return_value={"DELETE"}):
            mock_csv_reader_instance = MagicMock()
            mock_csv_reader_instance.__iter__.return_value = iter(MockFieldDictionaries.all_fields)
            process_csv_to_fhir(test_file.event_full_permissions_dict)

        mock_send_to_kinesis.assert_called()


if __name__ == "__main__":
    unittest.main()
