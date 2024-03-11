import os
import unittest

from immunisation_api import ImmunisationApi
from mesh import S3Service

source_bucket = "source-bucket"
destination_bucket = "destination-bucket"
csv_file_name = "data.csv"
csv_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data/{csv_file_name}"

sample_event = {
    "Records": [
        {
            "s3": {
                "bucket": {
                    "name": source_bucket,
                    "ownerIdentity": {"principalId": "A1XQJU98VTYE4Z"},
                    "arn": f"arn:aws:s3:::{source_bucket}",
                },
                "object": {
                    "key": csv_file_name,
                    "size": 1905,
                    "eTag": "7f3245332944742660f51cee091db9dc",
                    "sequencer": "006537C305E1353ABE",
                },
            },
        }
    ]
}


class TestBatchProcessing(unittest.TestCase):
    def setUp(self):
        self.sample_csv = ["field1", "field2"]
        self.imms_api = ImmunisationApi("https://example.com")
        self.s3_service = S3Service()
        self.event = sample_event
        self.context = {}

    def test_process_csv(self):
        pass

    def test_create_error_report(self):
        pass
