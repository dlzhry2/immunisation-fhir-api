import boto3
import pytest
from moto import mock_lambda,  mock_s3
from unittest import mock
import shutil
from icecream import ic

from backend.batch_processing_lambda.batch_processing import lambda_handler

@mock_lambda
def test_lambda_handler_400():
    # Empty event
    response = lambda_handler({}, {})
    assert response['statusCode'] == 400

@mock_lambda
@mock_s3
def test_lambda_handler_no_such_bucket():
    # Create buckets
    client = boto3.client('s3', region_name='eu-west-2')
    try:
        response = lambda_handler({
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": "source-bucket"
                        },
                        "object": {
                            "key": "source-key"
                        }
                    }
                }
            ]
        }, {})
        ic(response) #NWTMPXXX
    except client.exceptions.NoSuchBucket as err:
        ic(err)

@mock_lambda
@mock_s3
def test_lambda_handler():
    # Create buckets
    resource = boto3.resource('s3', region_name='eu-west-2')
    resource.create_bucket(Bucket='source-bucket', CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'})
    resource.create_bucket(Bucket='destination-bucket', CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'})

    response = lambda_handler({
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "source-bucket"
                    },
                    "object": {
                        "key": "source-key"
                    }
                }
            }
        ]
    }, {})
    ic(response) #NWTMPXXX
    assert response[0]['statusCode'] == 200
    assert response[0]['json']['id'] is not None
    assert response[0]['json']['message'] is not None