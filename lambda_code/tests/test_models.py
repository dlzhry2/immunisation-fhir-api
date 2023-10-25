import os
import sys
import unittest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models import MeshCsvContent

csv_file_name = "data2.csv"
csv_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data/{csv_file_name}"


class TestBatchProcessing(unittest.TestCase):
    def setUp(self):
        with open(csv_file_path, "r") as data:
            self.sample_csv = data.read()
            self.mesh_csv = MeshCsvContent()

    def test_parse_csv(self):
        records = MeshCsvContent.parse_from_csv(self.sample_csv)
        self.assertEqual(len(records), 2)
