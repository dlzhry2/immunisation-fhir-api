import os
import sys
import unittest

import responses

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from services import ImmunisationApi


class TestImmsApiService(unittest.TestCase):
    def setUp(self):
        self.imms_api = ImmunisationApi()

    @responses.activate
    def test_post_event(self):
        responses.add(responses.GET, 'http://twitter.com/api/1/foobar',
                      json={'error': 'not found'}, status=404)

        resp = self.imms_api.post_event(None, None)
        assert resp.json() == {"error": "not found"}
