import boto3
from utils.batch import get_s3_source_name


def test_s3_folder_structure():
    source_bucket = get_s3_source_name()
    s3 = boto3.client("s3")
    expected_folders = ["COVID19_POC/", "COVID19/", "FLU_POC/", "FLU/"]
    objects = s3.list_objects_v2(Bucket=source_bucket)
    actual_folders = [
        obj["Key"] for obj in objects.get("Contents", []) if obj["Key"].endswith("/")
    ]
    assert expected_folders == actual_folders
