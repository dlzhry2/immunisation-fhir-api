"""Tests for make_and_upload_ack_file functions"""

from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy
from boto3 import client as boto3_client
from moto import mock_s3

from make_and_upload_ack_file import make_the_ack_data, upload_ack_file, make_and_upload_the_ack_file
from clients import REGION_NAME
from tests.utils_for_tests.utils_for_filenameprocessor_tests import download_csv_file_as_dict_reader
from tests.utils_for_tests.values_for_tests import (
    MOCK_ENVIRONMENT_DICT,
    DESTINATION_BUCKET_NAME,
    VALID_FLU_EMIS_FILE_KEY,
    VALID_FLU_EMIS_ACK_FILE_KEY,
    STATIC_DATETIME_FORMATTED,
)


s3_client = boto3_client("s3", region_name=REGION_NAME)
MOCK_MESSAGE_ID = "test_id"
EXPECTED_ACK_DATA = {
    "MESSAGE_HEADER_ID": MOCK_MESSAGE_ID,
    "HEADER_RESPONSE_CODE": "Failure",
    "ISSUE_SEVERITY": "Fatal",
    "ISSUE_CODE": "Fatal Error",
    "ISSUE_DETAILS_CODE": "10001",
    "RESPONSE_TYPE": "Technical",
    "RESPONSE_CODE": "10002",
    "RESPONSE_DISPLAY": "Infrastructure Level Response Value - Processing Error",
    "RECEIVED_TIME": STATIC_DATETIME_FORMATTED,
    "MAILBOX_FROM": "",
    "LOCAL_ID": "",
    "MESSAGE_DELIVERY": False,
}


@mock_s3
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestMakeAndUploadAckFile(TestCase):
    """Tests for make_and_upload_ack_file functions"""

    def setUp(self):
        """Set up the bucket for the ack files"""
        s3_client.create_bucket(
            Bucket=DESTINATION_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": REGION_NAME}
        )

    def test_make_ack_data(self):
        "Tests make_ack_data makes correct ack data based on the input args"
        # CASE: message not delivered (this is the only case which creates an ack file for filenameprocessor)
        message_delivered = False
        self.assertEqual(
            make_the_ack_data(MOCK_MESSAGE_ID, message_delivered, STATIC_DATETIME_FORMATTED), EXPECTED_ACK_DATA
        )

    def test_upload_ack_file(self):
        """Test that upload_ack_file successfully uploads the ack file"""
        upload_ack_file(VALID_FLU_EMIS_FILE_KEY, EXPECTED_ACK_DATA, STATIC_DATETIME_FORMATTED)

        expected_result = [deepcopy(EXPECTED_ACK_DATA)]
        # Note that the data downloaded from the CSV will contain the bool as a string
        expected_result[0]["MESSAGE_DELIVERY"] = "False"
        csv_dict_reader = download_csv_file_as_dict_reader(
            s3_client, DESTINATION_BUCKET_NAME, VALID_FLU_EMIS_ACK_FILE_KEY
        )
        self.assertEqual(list(csv_dict_reader), expected_result)

    def test_make_and_upload_ack_file(self):
        """Test that make_and_upload_ack_file uploads an ack file containing the correct values"""
        message_delivered = False
        make_and_upload_the_ack_file(
            MOCK_MESSAGE_ID,
            VALID_FLU_EMIS_FILE_KEY,
            message_delivered,
            STATIC_DATETIME_FORMATTED,
        )

        expected_result = [deepcopy(EXPECTED_ACK_DATA)]
        expected_result[0]["MESSAGE_DELIVERY"] = "False"
        csv_dict_reader = download_csv_file_as_dict_reader(
            s3_client, DESTINATION_BUCKET_NAME, VALID_FLU_EMIS_ACK_FILE_KEY
        )
        self.assertEqual(list(csv_dict_reader), expected_result)
