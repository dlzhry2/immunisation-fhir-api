import unittest
from moto import mock_s3, mock_sqs
import boto3
import os
import json
from boto3 import client as boto3_client
from ack_processor import lambda_handler
from tests.utils_ack_processor import DESTINATION_BUCKET_NAME, AWS_REGION

s3_client = boto3_client("s3", region_name=AWS_REGION)
file_name = "COVID19_Vaccinations_v5_YGM41_20240909T13005901.csv"
ack_file_key = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240909T13005901_BusAck.csv"
local_id = "111^222"


@mock_s3
@mock_sqs
class TestAckProcessorE2E(unittest.TestCase):

    def setup_s3(self):
        """Helper to setup mock S3 buckets and upload test file"""
        s3_client.create_bucket(
            Bucket=DESTINATION_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
        )

    def invoke_lambda_and_verify_ack(self, event, expected_status, expected_messages):
        """
        Helper method to invoke Lambda and verify acknowledgment file content.
        :param event: The event to pass to the Lambda function
        :param expected_status: Expected HTTP status code in the Lambda response
        :param expected_messages: List of messages expected to be in the acknowledgment file
        """
        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], expected_status)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_content = (
            s3_client.get_object(Bucket=DESTINATION_BUCKET_NAME, Key=ack_file_key)["Body"].read().decode("utf-8")
        )

        # Assert acknowledgment file content
        for message in expected_messages:
            self.assertIn(message, ack_file_content)

    def test_ack_processor_invalid_action_flag(self):
        self.setup_s3()
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "row_id": "855d9cf2-31ef-44ef-8479-8785cf908759#1",
                            "file_key": file_name,
                            "supplier": "EMIS",
                            "created_at_formatted_string": "20241115T13435500",
                            "diagnostics": "Invalid ACTION_FLAG - ACTION_FLAG must be 'NEW', 'UPDATE' or 'DELETE'",
                            "operation_requested": "",
                            "local_id": local_id,
                        }
                    )
                }
            ]
        }
        self.invoke_lambda_and_verify_ack(
            event, 200, ["Fatal Error", "Invalid ACTION_FLAG - ACTION_FLAG must be 'NEW', 'UPDATE' or 'DELETE'"]
        )

    def test_ack_processor_imms_not_found(self):
        self.setup_s3()
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "row_id": "855d9cf2-31ef-44ef-8479-8785cf908759#1",
                            "file_key": file_name,
                            "supplier": "EMIS",
                            "created_at_formatted_string": "20241115T13435500",
                            "diagnostics": "Imms id not found",
                            "operation_requested": "",
                            "local_id": local_id,
                        }
                    )
                }
            ]
        }
        self.invoke_lambda_and_verify_ack(event, 200, ["Fatal Error", "Imms id not found"])

    def test_ack_processor_unique_id_or_uri_missing(self):
        self.setup_s3()
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "row_id": "855d9cf2-31ef-44ef-8479-8785cf908759#1",
                            "file_key": file_name,
                            "supplier": "EMIS",
                            "created_at_formatted_string": "20241115T13435500",
                            "diagnostics": "UNIQUE_ID or UNIQUE_ID_URI is missing",
                            "operation_requested": "",
                            "local_id": local_id,
                        }
                    )
                }
            ]
        }
        self.invoke_lambda_and_verify_ack(event, 200, ["Fatal Error", "UNIQUE_ID or UNIQUE_ID_URI is missing"])

    def test_ack_processor_create_success(self):
        self.setup_s3()
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "statusCode": 201,
                            "headers": {
                                "Location": "https://internal-dev.api.service.nhs.uk/immunisation-fhir-api/Immunization/719aef39-64b1-4e7b-981e-4acb64e8538e"
                            },
                            "file_key": file_name,
                            "row_id": "6cd75847-e378-451f-984e-b55fa5444b50#1",
                            "created_at_formatted_string": "20241119T11182100",
                        }
                    )
                }
            ]
        }
        self.invoke_lambda_and_verify_ack(event, 200, ["OK", "719aef39-64b1-4e7b-981e-4acb64e8538e"])

    def test_ack_processor_create_duplicate(self):
        self.setup_s3()
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "statusCode": 422,
                            "headers": {"Content-Type": "application/fhir+json"},
                            "body": json.dumps(
                                {
                                    "resourceType": "OperationOutcome",
                                    "id": "e51e9e59-4d57-41bc-b21f-5ef95547eaac",
                                    "meta": {
                                        "profile": [
                                            "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
                                        ]
                                    },
                                    "issue": [
                                        {
                                            "severity": "error",
                                            "code": "duplicate",
                                            "details": {
                                                "coding": [
                                                    {
                                                        "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                                                        "code": "DUPLICATE",
                                                    }
                                                ]
                                            },
                                            "diagnostics": (
                                                "The provided identifier: https://www.ravs.england.nhs.uk/#0001_RSV_v5_Run3_valid_dose_1_new_upd_del_20240905130057 is duplicated"
                                            ),
                                        }
                                    ],
                                }
                            ),
                            "file_key": file_name,
                            "row_id": "8fb764cf-93af-453f-9246-ea6cd6244069#1",
                            "created_at_formatted_string": "20241119T11554300",
                        }
                    )
                }
            ]
        }
        self.invoke_lambda_and_verify_ack(
            event,
            200,
            [
                "Fatal Error",
                "The provided identifier: https://www.ravs.england.nhs.uk/#0001_RSV_v5_Run3_valid_dose_1_new_upd_del_20240905130057 is duplicated",
            ],
        )

    def test_ack_processor_update_and_delete_success(self):
        self.setup_s3()
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "statusCode": 200,
                            "headers": {},
                            "file_key": file_name,
                            "row_id": "565d8c47-25ee-4958-a59b-3a4fc0e8c6da#1",
                            "created_at_formatted_string": "20241119T11344900",
                            "local_id": local_id,
                        }
                    )
                }
            ]
        }
        self.invoke_lambda_and_verify_ack(event, 200, ["OK"])

    def tearDown(self):
        # Clean up mock resources
        os.environ.pop("ACK_BUCKET_NAME", None)
