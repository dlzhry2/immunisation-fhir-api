import unittest
import sys
import os
import json
from icecream import ic

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.fhir_immunization import ImmunizationValidator


class TestImmsValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.data_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_data"
        self.file_path = f"{self.data_path}/sample_event3.json"
        with open(self.file_path, "r") as f:
            self.json_data = json.load(f)

        # ic(self.json_data["patient"]["identifier"]["value"])

    def test_validate(self):
        immunization_validator = ImmunizationValidator(self.json_data)
        immunization_validator.validate()
