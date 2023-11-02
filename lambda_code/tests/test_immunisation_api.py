import os
import sys
import unittest

import responses
from responses import matchers

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from immunisation_api import ImmunisationApi, create_response


class TestRequestResponseHelpers(unittest.TestCase):
    def test_create_response(self):
        res = create_response(42, "a body")
        headers = res["headers"]
        self.assertEqual(res["statusCode"], 42)

        self.assertDictEqual(headers, {
            "Content-Type": "application/fhir+json",
        })
        self.assertEqual(res["body"], "a body")


class TestImmsApiService(unittest.TestCase):
    def setUp(self):
        self.url = "https://example.com"
        self.imms_api = ImmunisationApi(self.url)

    @responses.activate
    def test_post_event(self):
        act_res = {"response": "OK"}
        payload = {"foo": "bar"}
        exp_header = {
            "Content-Type": "application/fhir+json",
        }
        responses.add(responses.POST, f"{self.url}/event",
                      json=act_res, status=201,
                      match=[matchers.json_params_matcher(payload), matchers.header_matcher(exp_header)])

        resp = self.imms_api.post_event(payload)
        self.assertEqual(resp.json(), act_res)
