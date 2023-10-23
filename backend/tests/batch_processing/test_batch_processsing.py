""" Tests for the batch_processing lambda """

import boto3
import pytest

from moto import mock_s3
from backend.batch_processing_lambda.batch_processing import lambda_handler


# Status code tests
@mock_s3
def test_processing_lambda_200():
    """Test that the lambda returns a 200 status code when the event is valid"""
    # Create buckets
    resource = boto3.resource("s3", region_name="eu-west-2")
    resource.create_bucket(
        Bucket="source-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )
    resource.create_bucket(
        Bucket="destination-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )

    # Call lambda
    response = lambda_handler(
        {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "source-bucket"},
                        "object": {"key": "source-key"},
                    }
                }
            ]
        },
        {},
    )

    assert response[0]["statusCode"] == 200
    assert response[0]["json"]["id"] is not None
    assert response[0]["json"]["message"] is not None


def test_batch_processing_lambda_400():
    """Test that the lambda returns a 400 status code when the event is invalid"""
    # Call lambda with empty event
    response = lambda_handler({}, {})
    assert response["statusCode"] == 400


# Exception tests
@mock_s3
def test_batch_processing_lambda_no_such_bucket():
    """
    Test that the lambda raises a NoSuchBucket exception when the source bucket does not exist
    """
    client = boto3.client("s3", region_name="eu-west-2")
    with pytest.raises(client.exceptions.NoSuchBucket):
        lambda_handler(
            {
                "Records": [
                    {
                        "s3": {
                            "bucket": {"name": "source-bucket"},
                            "object": {"key": "source-key"},
                        }
                    }
                ]
            },
            {},
        )
