"""Utils functions for filenameprocessor tests"""

from io import StringIO
import json
from csv import DictReader
from boto3 import client as boto3_client
from tests.utils_for_tests.values_for_tests import VALID_FILE_CONTENT


def setup_s3_bucket_and_file(
    test_bucket_name: str, test_file_key: str, test_file_content: str = VALID_FILE_CONTENT
) -> None:
    """
    Sets up the S3 client and uploads the test file, containing the test file content, to a bucket named 'test_bucket'
    """
    s3_client = boto3_client("s3", region_name="eu-west-2")
    s3_client.create_bucket(Bucket=test_bucket_name, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
    s3_client.put_object(Bucket=test_bucket_name, Key=test_file_key, Body=test_file_content)


def download_csv_file_as_dict_reader(s3_client, bucket_name: str, file_key: str) -> DictReader:
    """Download the file from the S3 bucket and return it as a DictReader"""
    ack_file_csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    csv_content_string = ack_file_csv_obj["Body"].read().decode("utf-8")
    return DictReader(StringIO(csv_content_string), delimiter="|")


def generate_permissions_config_content(permissions_dict: dict) -> str:
    """Converts the permissions dictionary to a JSON string"""
    return json.dumps({"all_permissions": permissions_dict})
