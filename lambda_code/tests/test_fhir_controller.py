import os
import sys
import unittest
from unittest.mock import create_autospec

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_controller import FhirController
from fhir_service import FhirService


class TestFhirController(unittest.TestCase):
    def setUp(self):
        self.service = create_autospec(FhirService)
        self.controller = FhirController(self.service)

    def test_create_response(self):
        """it should return application/fhir+json with correct status code"""
        res = self.controller._create_response(42, "a body")
        headers = res["headers"]

        self.assertEqual(res["statusCode"], 42)
        self.assertDictEqual(headers, {
            "Content-Type": "application/fhir+json",
        })
        self.assertEqual(res["body"], "a bodys")
