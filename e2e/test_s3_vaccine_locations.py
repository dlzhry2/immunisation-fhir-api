import boto3
import unittest
from utils.batch import get_s3_source_name

class TestS3Batch(unittest.TestCase):

    def test_s3_folder_structure(self):
        source_bucket = get_s3_source_name()
        print(f"source bucket: {source_bucket}")
        s3 = boto3.client("s3")
        expected_folders = ["COVID19_POC/", "COVID19/", "FLU_POC/", "FLU/"]
        objects = s3.list_objects_v2(Bucket=source_bucket)
        actual_folders = [
            obj["Key"] for obj in objects.get("Contents", []) if obj["Key"].endswith("/")
        ]
        assert expected_folders == actual_folders


if __name__ == "__main__":
    unittest.main()