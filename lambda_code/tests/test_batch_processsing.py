""" Tests for the batch_processing lambda """

from unittest.mock import MagicMock

import boto3
import pytest
from moto import mock_s3

from lambda_code.src.batch_processing_handler import batch_processing_handler
from lambda_code.src.immunisation_api import ImmunisationAPI


@mock_s3
def test_batch_processing():
    mock_api = ImmunisationAPI()
    mock_api.post_event = MagicMock(return_value={})
    event = {
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

    assert response[0]["statusCode"] == 200

    # mock_api.post_event.assert_called_with(event)


## Status code tests
# @mock_s3
# def test_processing_lambda_200():
#    """Test that the lambda returns a 200 status code when the event is valid"""
#    # Create buckets
#    resource = boto3.resource("s3", region_name="eu-west-2")
#    resource.create_bucket(
#        Bucket="source-bucket",
#        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
#    )
#    resource.create_bucket(
#        Bucket="destination-bucket",
#        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
#    )
#
#    # Call lambda
#    response = batch_processing_handler(
#        {
#            "Records": [
#                {
#                    "s3": {
#                        "bucket": {"name": "source-bucket"},
#                        "object": {"key": "source-key"},
#                    }
#                }
#            ]
#        },
#        {},
#    )
#
#    assert response[0]["statusCode"] == 200
#    assert response[0]["json"]["id"] is not None
#    assert response[0]["json"]["message"] is not None
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
