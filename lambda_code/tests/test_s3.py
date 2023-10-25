import os
import sys
import unittest

import boto3
from moto import mock_s3

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from services import S3Service


class TestBatchProcessing(unittest.TestCase):

    def create_s3_bucket(self):
        self.bucket_name = "my-bucket"
        self.act_body = "my-content"
        self.act_key = "my-key"

        s3_client = boto3.resource("s3", region_name="eu-west-2")
        return s3_client.create_bucket(
            Bucket=self.bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )

    @mock_s3
    def test_get_s3_object(self):
        s3_bucket = self.create_s3_bucket()
        s3_bucket.put_object(Body=self.act_body, Key=self.act_key)

        data = S3Service.get_s3_object(self.bucket_name, self.act_key)

        self.assertEqual(data, self.act_body)

    @mock_s3
    def test_write_s3_object(self):
        self.create_s3_bucket()

        S3Service.write_s3_object(self.bucket_name, self.act_key, self.act_body)
        data = S3Service.get_s3_object(self.bucket_name, self.act_key)

        self.assertEqual(data, self.act_body)
