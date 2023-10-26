""" Tests for the batch_processing lambda """
import os.path
import sys

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

import boto3

from batch_processing_handler import batch_processing_handler


# from lambda_code.src.batch_processing_handler import batch_processing_handler, batch_processing


# from lambda_code.src.services import ImmunisationAPI, S3Service


def nathan():
    # Create buckets
    resource = boto3.resource("s3", region_name="eu-west-2")
    resource.create_bucket(
        Bucket="immunisation-fhir-api-nawa1-batch-data-source",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )
    resource.create_bucket(
        Bucket="immunisation-fhir-api-nawa1-batch-data-destination",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )

    response = batch_processing_handler(event, {}, mock_api)


SAMPLE_EVENT = {
    "Records": [
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "eu-west-2",
            "eventTime": "2023-10-24T13:13:41.935Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "AWS:AROA3P5FMCZ5RLJE6ZD4N:nathan.wall1"
            },
            "requestParameters": {"sourceIPAddress": "63.135.74.250"},
            "responseElements": {
                "x-amz-request-id": "183BM3195G6PXRKV",
                "x-amz-id-2": "aMTHQCGYevtkXnMFqGIBoYh4gfKV9rV871vK9JsNhNgPbnn4+Fi2FBhKHFe48m7QVPOkNocdHNWOSoyPww8go1vyWr1jerrx",
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "tf-s3-lambda-20231023105022550100000001",
                "bucket": {
                    "name": "immunisation-fhir-api-nawa1-batch-data-source",
                    "ownerIdentity": {"principalId": "A1XQJU98VTYE4Z"},
                    "arn": "arn:aws:s3:::immunisation-fhir-api-nawa1-batch-data-source",
                },
                "object": {
                    "key": "patient_data.csv",
                    "size": 1905,
                    "eTag": "7f3245332944742660f51cee091db9dc",
                    "sequencer": "006537C305E1353ABE",
                },
            },
        }
    ]
}

# @mock_s3
# def test_batch_processing():
#     mock_api = ImmunisationAPI()
#     mock_api.post_event = MagicMock(return_value={})
#     s3_service = S3Service("source", "destination")
#     s3_service.get_key_data = MagicMock(return_value=[{"patient": 123}])
#
#     batch_processing(SAMPLE_EVENT, {}, s3_service, mock_api)
#
#     s3_service.get_key_data.assert_called_with("patient_data.csv")
#     mock_api.post_event.assert_called_with({"patient": 123})
#
#
# def test_batch_error_report():
#     mock_api = ImmunisationAPI()
#     mock_api.post_event = MagicMock(return_value={"statusCode": 400})
#     s3_service = S3Service("source", "destination")
#     s3_service.get_key_data = MagicMock(return_value=[{"patient": 123}])
#     s3_service.write_report = MagicMock(return_value=["error"])
#
#     batch_processing(SAMPLE_EVENT, {}, s3_service, mock_api)
#
#     mock_api.post_event.assert_called_with({"patient": 123})
#     s3_service.write_report.assert_called_with(["error"])
#
# ## Status code tests
# @mock_s3
# def test_processing_lambda_200():
#     """Test that the lambda returns a 200 status code when the event is valid"""
#     # Create buckets
#     resource = boto3.resource("s3", region_name="eu-west-2")
#     resource.create_bucket(
#         Bucket="source-bucket",
#         CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
#     )
#     resource.create_bucket(
#         Bucket="destination-bucket",
#         CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
#     )
#
#     # Call lambda
#     response = batch_processing_handler(
#         {
#             "Records": [
#                 {
#                     "s3": {
#                         "bucket": {"name": "source-bucket"},
#                         "object": {"key": "source-key"},
#                     }
#                 }
#             ]
#         },
#         {},
#     )
#
#     assert response[0]["statusCode"] == 200
#     assert response[0]["json"]["id"] is not None
#     assert response[0]["json"]["message"] is not None
#
#
# def test_batch_processing_lambda_400():
#    """Test that the lambda returns a 400 status code when the event is invalid"""
#    # Call lambda with empty event
#    response = batch_processing_handler({}, {})
#    assert response["statusCode"] == 400
#
#
## Exception tests
# @mock_s3
# def test_batch_processing_lambda_no_such_bucket():
#    """
#    Test that the lambda raises a NoSuchBucket exception when the source bucket does not exist
#    """
#    client = boto3.client("s3", region_name="eu-west-2")
#    with pytest.raises(client.exceptions.NoSuchBucket):
#        batch_processing_handler(
#            {
#                "Records": [
#                    {
#                        "s3": {
#                            "bucket": {"name": "source-bucket"},
#                            "object": {"key": "source-key"},
#                        }
#                    }
#                ]
#            },
#            {},
#        )
