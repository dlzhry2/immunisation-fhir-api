"""Tests for the logging_decorator and its helper functions"""

import unittest
from unittest.mock import patch
from datetime import datetime
import json
from copy import deepcopy
from boto3 import client as boto3_client
from moto import mock_s3, mock_firehose
from file_level_validation import file_level_validation
from clients import REGION_NAME
from errors import InvalidHeaders, NoOperationPermissions
from tests.utils_for_recordprocessor_tests.values_for_recordprocessor_tests import (
    MOCK_ENVIRONMENT_DICT,
    MockFileDetails,
    BucketNames,
    ValidMockFileContent,
    Firehose,
)
from tests.utils_for_recordprocessor_tests.utils_for_recordprocessor_tests import GenericSetUp, GenericTearDown

s3_client = boto3_client("s3", region_name=REGION_NAME)
firehose_client = boto3_client("firehose", region_name=REGION_NAME)
MOCK_FILE_DETAILS = MockFileDetails.flu_emis
COMMON_LOG_DATA = {
    "function_name": "record_processor_file_level_validation",
    "date_time": "2024-01-01 12:00:00",  # (tests mock a 2024-01-01 12:00:00 datetime)
    "time_taken": "0.12346s",  # Time taken is rounded to 5 decimal places (tests mock a 0.123456s time taken)
    "file_key": MOCK_FILE_DETAILS.file_key,
    "message_id": MOCK_FILE_DETAILS.message_id,
    "vaccine_type": MOCK_FILE_DETAILS.vaccine_type,
    "supplier": MOCK_FILE_DETAILS.supplier,
}


@mock_s3
@mock_firehose
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestLoggingDecorator(unittest.TestCase):
    """Tests for the logging_decorator and its helper functions"""

    def setUp(self):
        """Set up the S3 buckets and upload the valid FLU/EMIS file example"""
        GenericSetUp(s3_client, firehose_client)

    def tearDown(self):
        GenericTearDown(s3_client, firehose_client)

    def test_splunk_logger_successful_validation(self):
        """Tests the splunk logger is called when file-level validation is successful"""

        s3_client.put_object(
            Bucket=BucketNames.SOURCE,
            Key=MOCK_FILE_DETAILS.file_key,
            Body=ValidMockFileContent.with_new_and_update_and_delete,
        )

        with (
            patch("logging_decorator.datetime") as mock_datetime,
            patch("logging_decorator.time") as mock_time,
            patch("logging_decorator.logger") as mock_logger,
            patch("logging_decorator.firehose_client") as mock_firehose_client,
        ):
            mock_time.time.side_effect = [1672531200, 1672531200.123456]
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
            file_level_validation(deepcopy(MOCK_FILE_DETAILS.event_full_permissions_dict))

        expected_message = (
            "File headers validated and supplier has permission to perform at least one of the "
            + "requested operations"
        )
        expected_log_data = {**COMMON_LOG_DATA, "statusCode": 200, "message": expected_message}

        # Log data is the first positional argument of the first call to logger.info
        log_data = json.loads(mock_logger.info.call_args_list[0][0][0])
        self.assertEqual(log_data, expected_log_data)

        expected_firehose_record = {"Data": json.dumps({"event": log_data}).encode("utf-8")}
        mock_firehose_client.put_record.assert_called_once_with(
            DeliveryStreamName=Firehose.STREAM_NAME, Record=expected_firehose_record
        )

    def test_splunk_logger_failure(self):
        """Tests the splunk logger is called when file-level validation fails"""

        # Test case tuples are structured as (file_content, event_dict, expected_error_type,
        # expected_status_code, expected_message, expected_error_message)
        test_cases = [
            # CASE: Invalid headers
            (
                ValidMockFileContent.with_new_and_update_and_delete.replace("NHS_NUMBER", "NHS_NUMBERS"),
                MOCK_FILE_DETAILS.event_full_permissions_dict,
                InvalidHeaders,
                400,
                "File headers are invalid.",
                "File headers are invalid.",
            ),
            # CASE: No operation permissions
            (
                ValidMockFileContent.with_new_and_update,
                MOCK_FILE_DETAILS.event_delete_permissions_only_dict,  # No permission for NEW or UPDATE
                NoOperationPermissions,
                403,
                f"{MOCK_FILE_DETAILS.supplier} does not have permissions to perform any of the requested actions.",
                f"{MOCK_FILE_DETAILS.supplier} does not have permissions to perform any of the requested actions.",
            ),
            # TOD0: ?Server error
        ]

        for (
            mock_file_content,
            event_dict,
            expected_error_type,
            expected_status_code,
            expected_message,
            expected_error,
        ) in test_cases:
            with self.subTest(expected_error):

                s3_client.put_object(Bucket=BucketNames.SOURCE, Key=MOCK_FILE_DETAILS.file_key, Body=mock_file_content)

                with (
                    patch("logging_decorator.datetime") as mock_datetime,
                    patch("logging_decorator.time") as mock_time,
                    patch("logging_decorator.logger") as mock_logger,
                    patch("logging_decorator.firehose_client") as mock_firehose_client,
                ):
                    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
                    mock_time.time.side_effect = [1672531200, 1672531200.123456]
                    with self.assertRaises(expected_error_type):
                        file_level_validation(deepcopy(event_dict))

                expected_log_data = {
                    **COMMON_LOG_DATA,
                    "statusCode": expected_status_code,
                    "message": expected_message,
                    "error": expected_error,
                }

                # Log data is the first positional argument of the first call to logger.error
                log_data = json.loads(mock_logger.error.call_args_list[0][0][0])
                self.assertEqual(log_data, expected_log_data)

                expected_firehose_record = {"Data": json.dumps({"event": log_data}).encode("utf-8")}
                mock_firehose_client.put_record.assert_called_once_with(
                    DeliveryStreamName=Firehose.STREAM_NAME, Record=expected_firehose_record
                )
