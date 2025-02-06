from unittest.mock import patch
from tests.utils_for_tests.values_for_tests import BucketNames, MOCK_ENVIRONMENT_DICT

with patch.dict("os.environ", MOCK_ENVIRONMENT_DICT):
    from clients import REGION_NAME


class GenericSetUp:
    """
    Performs generic setup of mock resources:
    * If s3_client is provided, creates source, destination and firehose buckets (firehose bucket is used for testing
        only)
    * If firehose_client is provided, creates a firehose delivery stream
    """

    def __init__(self, s3_client=None):

        if s3_client:
            for bucket_name in [BucketNames.SOURCE, BucketNames.DESTINATION, BucketNames.CONFIG]:
                s3_client.create_bucket(
                    Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": REGION_NAME}
                )


class GenericTearDown:
    """Performs generic tear down of mock resources"""

    def __init__(self, s3_client=None):

        if s3_client:
            for bucket_name in [BucketNames.SOURCE, BucketNames.DESTINATION]:
                for obj in s3_client.list_objects_v2(Bucket=bucket_name).get("Contents", []):
                    s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
                s3_client.delete_bucket(Bucket=bucket_name)
