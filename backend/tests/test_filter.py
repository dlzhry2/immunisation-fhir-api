"""Tests for Filter class"""

from copy import deepcopy
from uuid import uuid4

import unittest

from src.filter import (
    Filter,
    remove_reference_to_contained_practitioner,
    create_reference_to_patient_resource,
    add_use_to_identifier,
)
from tests.utils.generic_utils import load_json_data


class TestFilter(unittest.TestCase):
    """Test for Filter class"""

    def setUp(self):
        self.covid_19_immunization_event = load_json_data("completed_covid19_immunization_event.json")
        self.bundle_patient_resource = load_json_data("bundle_patient_resource.json")

    def test_remove_reference_to_contained_practitioner(self):
        """Tests to ensure remove_refernce_to_contained_practitioner correctly removes the reference"""

        # TEST CASE: contained practitioner exists
        input_data = {
            "resourceType": "Immunization",
            "contained": [
                {"resourceType": "Patient", "id": "Pat1"},
                {"resourceType": "Practitioner", "id": "Pract1"},
            ],
            "performer": [
                {"actor": {"type": "Organization"}},
                {"actor": {"reference": "#Pract1"}},
                {"actor": {"reference": "NOT AN INTERNAL REFERENCE"}},
            ],
        }

        expected_output = {
            "resourceType": "Immunization",
            "contained": [
                {"resourceType": "Patient", "id": "Pat1"},
                {"resourceType": "Practitioner", "id": "Pract1"},
            ],
            "performer": [
                {"actor": {"type": "Organization"}},
                {"actor": {"reference": "NOT AN INTERNAL REFERENCE"}},
            ],
        }

        self.assertEqual(remove_reference_to_contained_practitioner(input_data), expected_output)

        # TEST CASE: contained practitioner does not exist
        input_data = {
            "resourceType": "Immunization",
            "contained": [{"resourceType": "Patient", "id": "Pat1"}],
            "performer": [
                {"actor": {"type": "Organization"}},
                {"actor": {"reference": "NOT AN INTERNAL REFERENCE"}},
            ],
        }

        expected_output = deepcopy(input_data)

        self.assertEqual(remove_reference_to_contained_practitioner(input_data), expected_output)

    def test_create_reference_to_patient_resource(self):
        """Test that create_reference_to_patient_resource creates an appropriate patient reference"""
        input_data = deepcopy(self.bundle_patient_resource)
        patient_uuid = str(uuid4())
        expected_output = {
            "reference": patient_uuid,
            "type": "Patient",
            "identifier": {"system": "https://fhir.nhs.uk/Id/nhs-number", "value": "9000000009"},
        }

        self.assertEqual(create_reference_to_patient_resource(patient_uuid, input_data), expected_output)

    def test_add_use_to_identifier(self):
        """Test that a use of "offical" is added to identifier[0] is no use already given"""
        input_data = deepcopy(self.covid_19_immunization_event)
        excepted_output = deepcopy(self.covid_19_immunization_event)
        excepted_output["identifier"][0]["use"] = "official"

        self.assertEqual(add_use_to_identifier(input_data), excepted_output)

    def test_filter_read(self):
        """Tests to ensure Filter.read appropriately filters a FHIR Immunization Resource"""
        unfiltered_imms = deepcopy(self.covid_19_immunization_event)
        expected_output = load_json_data("completed_covid19_immunization_event_filtered_for_read.json")
        self.assertEqual(Filter.read(unfiltered_imms), expected_output)

    def test_filter_search(self):
        """Tests to ensure Filter.search appropriately filters a FHIR Immunization Resource"""
        bundle_patient = deepcopy(self.bundle_patient_resource)
        patient_uuid = str(uuid4())
        unfiltered_imms = deepcopy(self.covid_19_immunization_event)
        expected_output = load_json_data(
            "completed_covid19_immunization_event_filtered_for_search_using_bundle_patient_resource.json"
        )
        expected_output["patient"]["reference"] = patient_uuid

        self.assertEqual(Filter.search(unfiltered_imms, patient_uuid, bundle_patient), expected_output)
