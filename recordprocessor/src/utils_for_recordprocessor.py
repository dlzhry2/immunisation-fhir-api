"""Utils for filenameprocessor lambda"""

from csv import DictReader
from io import StringIO
from s3_clients import s3_client


def get_csv_content_dict_reader(bucket_name: str, file_key: str) -> DictReader:
    """Returns the requested file contents in the form of a DictReader"""
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    csv_data = response["Body"].read().decode("utf-8")
    return DictReader(StringIO(csv_data), delimiter="|"), csv_data


def convert_string_to_dict_reader(data_string: str):
    """Take a data string and convert it to a csv DictReader"""
    return DictReader(StringIO(data_string), delimiter="|")
