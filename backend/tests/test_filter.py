"""Tests for Filter class"""

import unittest

from src.filter import Filter
from tests.utils.generic_utils import load_json_data


class TestFilter(unittest.TestCase):
    """Test for Filter class"""

    def test_filter_read(self):
        """Tests to ensure Filter.read appropriately filters a FHIR Immunization Resource"""
        unfiltered_imms = load_json_data("completed_covid19_immunization_event.json")
        expected_output = load_json_data("completed_covid19_immunization_event_for_read_return.json")
        self.assertEqual(Filter.read(unfiltered_imms), expected_output)
