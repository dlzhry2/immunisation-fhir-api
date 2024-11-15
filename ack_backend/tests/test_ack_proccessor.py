import unittest
from moto import mock_s3, mock_sqs
import boto3
import os
import json
from ack_processor import lambda_handler


class TestAckProcessorE2E(unittest.TestCase):

    @mock_s3
    @mock_sqs
    def setUp(self):
        # Set up mock S3 and SQS
        self.s3 = boto3.client("s3", region_name="eu-west-2")
        self.sqs = boto3.client("sqs", region_name="eu-west-2")

        # Create mock buckets
        self.s3.create_bucket(Bucket="immunisation-batch-internal-dev-data-sources", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        self.s3.create_bucket(
            Bucket="immunisation-batch-internal-dev-data-destination", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
        )

        # Add a sample source file to the source bucket
        self.s3.put_object(
            Bucket="immunisation-batch-internal-dev-data-sources",
            Key="test.csv",
            Body="Header1|Header2\nRow1|Value1\nRow2|Value2\n",
        )

        # Create mock SQS queue
        self.queue_url = self.sqs.create_queue(QueueName="test-queue")["QueueUrl"]

    @mock_s3
    @mock_sqs
    def test_e2e_ack_processor(self):
        # Add a message to the SQS queue
        # Simulate event for Lambda
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "Filename": "test.csv",
                            "MessageId": "1234",
                            "statusCode": 201,
                            "headers": {"Location": "https://internal-dev.api.service.nhs.uk/immunisation-fhir-api/Immunization/2a8d3663-958f-4724-82c8-8a55c34dba98"},
                        }
                    )
                }
            ]
        }

        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_key = "forwardedFile/test_BusAck.csv"
        ack_file_content = self.s3.get_object(Bucket="ack-bucket", Key=ack_file_key)["Body"].read().decode("utf-8")

        # Assert acknowledgment file content
        self.assertIn("1234", ack_file_content)  # Check row ID
        self.assertIn("OK", ack_file_content)  # Check response code
        self.assertIn("5678", ack_file_content)  # Check IMMS ID

    @mock_s3
    @mock_sqs
    def tearDown(self):
        # Clean up mock resources
        os.environ.pop("ACK_BUCKET_NAME", None)
        os.environ.pop("SOURCE_BUCKET_NAME", None)


if __name__ == "__main__":
    unittest.main()
