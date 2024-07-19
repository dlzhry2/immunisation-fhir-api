"""Tests for Filter class"""

from copy import deepcopy

import unittest

from src.constants import Urls
from src.filter import (
    Filter,
    remove_reference_to_contained_practitioner,
    create_reference_to_patient_resource,
    replace_address_postal_codes,
    replace_organization_values,
)
from tests.utils.generic_utils import load_json_data


class TestFilter(unittest.TestCase):
    """Test for Filter class"""

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
        input_data = load_json_data("bundle_patient_resource.json")
        expected_output = {
            "reference": "MOCK REFERENCE",
            "type": "Patient",
            "identifier": {"system": "https://fhir.nhs.uk/Id/nhs-number", "value": "9000000009"},
        }

        self.assertEqual(create_reference_to_patient_resource(input_data), expected_output)

    def test_replace_address_postal_codes(self):
        """Test that replace_address_postal_codes replaces the postal codes and leaves all other data unaltered"""
        input_imms = load_json_data("completed_covid19_immunization_event.json")
        expected_output = deepcopy(input_imms)
        expected_output["contained"][1]["address"][0]["postalCode"] = "ZZ99 3CZ"

        self.assertEqual(replace_address_postal_codes(input_imms), expected_output)

    def test_replace_organziation_values(self):
        """
        Test that replace_organziation_values replaces the relevant organization values and leave all other data
        unaltered
        """
        # Prepare the input data
        input_imms = load_json_data("completed_covid19_immunization_event.json")
        # Change the input data's organization_identifier_system to be something other than the ods url
        input_imms["performer"][1]["actor"]["identifier"]["system"] = Urls.urn_school_number
        # Add organization_display to the input data (note that whilst this field is not one of the expected fields,
        # the validator does not prevent it from being included on a create or update, so the possiblity of it
        # existing must be handled)
        input_imms["performer"][1]["actor"]["display"] = "test"

        # Prepare the expected_output
        expected_output = deepcopy(input_imms)
        expected_output["performer"][1]["actor"]["identifier"]["system"] = Urls.ods_organization_code
        expected_output["performer"][1]["actor"]["identifier"]["value"] = "N2N9I"
        del expected_output["performer"][1]["actor"]["display"]

        self.assertEqual(replace_organization_values(input_imms), expected_output)

    def test_filter_read(self):
        """Tests to ensure Filter.read appropriately filters a FHIR Immunization Resource"""
        unfiltered_imms = load_json_data("completed_covid19_immunization_event.json")
        expected_output = load_json_data("completed_covid19_immunization_event_filtered_for_read.json")
        self.assertEqual(Filter.read(unfiltered_imms), expected_output)

    def test_filter_search(self):
        """Tests to ensure Filter.search appropriately filters a FHIR Immunization Resource"""
        bundle_patient = load_json_data("bundle_patient_resource.json")
        unfiltered_imms = load_json_data("completed_covid19_immunization_event.json")
        expected_output = load_json_data(
            "completed_covid19_immunization_event_filtered_for_search_using_bundle_patient_resource.json"
        )
        self.assertEqual(Filter.search(unfiltered_imms, bundle_patient), expected_output)
