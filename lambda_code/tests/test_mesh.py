import copy
import os
import sys
import unittest

import boto3
from moto import mock_s3

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from mesh import MeshInputHandler, MeshOutputHandler, MeshCsvParser, MeshImmunisationReportEntry

sample_event = {
    "Records": [
        {
            "s3": {
                "bucket": {
                    "name": "a-bucket",
                    "ownerIdentity": {"principalId": "A1XQJU98VTYE4Z"},
                    "arn": f"arn:aws:s3:::a-bucket",
                },
                "object": {
                    "key": "a-key",
                    "size": 1905,
                    "eTag": "7f3245332944742660f51cee091db9dc",
                    "sequencer": "006537C305E1353ABE",
                },
            },
        }
    ]
}


def create_an_event_record(bucket_name, key):
    """create ONE fake record and NOT the entire event object"""
    record = copy.copy(sample_event)["Records"][0]
    record["s3"]["bucket"]["name"] = bucket_name
    record["s3"]["object"]["key"] = key

    return record


def create_a_bucket(name):
    s3_client = boto3.resource("s3", region_name="eu-west-2")
    return s3_client.create_bucket(Bucket=name,
                                   CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})


class TestMeshInputHandler(unittest.TestCase):
    def setUp(self):
        self.bucket = "input-bucket"
        self.key = "input-key"
        self.content = "input-content"
        self.event_record = create_an_event_record(self.bucket, self.key)

        self.mesh_input = MeshInputHandler(self.event_record)

    @mock_s3
    def test_get_event_content(self):
        input_bucket = create_a_bucket(self.bucket)
        input_bucket.put_object(Body=self.content, Key=self.key)

        data = self.mesh_input.get_event_content()

        self.assertEqual(data, self.content)


class TestMeshOutputHandler(unittest.TestCase):
    def setUp(self):
        self.bucket = "output-bucket"
        self.key = "output-key"
        self.content = "output-content"

        self.mesh_output = MeshOutputHandler(self.bucket, self.key)

    def test_write_to_s3(self):
        output_bucket = create_a_bucket(self.bucket)
        records = [MeshImmunisationReportEntry("error1"), MeshImmunisationReportEntry("error2"), ]
        # TODO: create a method here to read the object. make this to test if write_report is working.
        self.mesh_output.write_report(records)


csv_file_name = "data2.csv"
csv_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data/{csv_file_name}"


class TestMeshCsvParser(unittest.TestCase):
    def setUp(self):
        with open(csv_file_path, "r") as data:
            self.sample_csv = data.read()

    def test_parse_csv(self):
        mesh_csv = MeshCsvParser("data.csv", self.sample_csv)
        records = mesh_csv.parse()
        self.assertEqual(len(records), 2)
