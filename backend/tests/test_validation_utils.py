import unittest
from unittest.mock import MagicMock
from copy import deepcopy
from base_utils.base_utils import obtain_field_location
from models.field_locations import FieldLocations
from src.models.fhir_immunization import ImmunizationValidator
from .utils.generic_utils import (
    # these have an underscore to avoid pytest collecting them as tests
    test_valid_values_accepted as _test_valid_values_accepted,
    test_invalid_values_rejected as _test_invalid_values_rejected,
    load_json_data,
)
from src.mappings import VaccineTypes
from .utils.values_for_tests import ValidValues, InvalidValues
from models.utils.generic_utils import (
    get_current_name_instance,
    obtain_current_name_period,
    patient_and_practitioner_value_and_index,
    obtain_name_field_location,
)
from jsonpath_ng.ext import parse
from datetime import datetime


class TestValidatorUtils(unittest.TestCase):
    """Test immunization pre and post validation utils on the FHIR model"""

    def setUp(self):
        """Set up for each test. This runs before every test"""
        self.json_data = load_json_data(filename="completed_rsv_immunization_event.json")
        self.validator = ImmunizationValidator(add_post_validators=False)
        self.updated_json_data = parse("contained[?(@.resourceType=='Patient')].name").update(
            deepcopy(self.json_data), ValidValues.valid_name_4_instances
        )
        self.updated_PatientandPractitioner_json = parse("contained[?(@.resourceType=='Practitioner')].name").update(
            deepcopy(self.updated_json_data), ValidValues.valid_name_4_instances_practitioner
        )

    def test_get_current_name_instance_single_name(self):
        """Tests a single name occurrence"""
        names = [ValidValues.valid_name_4_instances[2]]
        occurrence_date = ValidValues.for_occurrenceDateTime
        result = get_current_name_instance(names, occurrence_date)
        self.assertEqual(result, (0, {"family": "Taylor", "given": ["Sar"]}))

    def test_get_current_name_instance_multiple_names(self):
        """Tests a multiple name occurrences"""
        names = ValidValues.valid_name_4_instances
        occurrence_date = ValidValues.for_occurrenceDateTime
        result = get_current_name_instance(names, occurrence_date)
        self.assertEqual(result, (1, ValidValues.valid_name_4_instances[1]))

    def test_no_official_names_or_period(self):
        """Tests obtaining current name if no official name or period exists"""
        names = [ValidValues.valid_name_4_instances[2], ValidValues.valid_name_4_instances[3]]
        occurrence_date = ValidValues.for_occurrenceDateTime
        result = get_current_name_instance(names, occurrence_date)
        self.assertEqual(result, (0, {"family": "Taylor", "given": ["Sar"]}))

    def test_obtain_current_name_period(self):
        """Test obtaining current name based on period."""
        # name with vaccine date between current period (start and end)
        valid_name = ValidValues.valid_name_4_instances[1]
        current_name = obtain_current_name_period(valid_name["period"], ValidValues.for_occurrenceDateTime)
        self.assertTrue(current_name)

        # name with expired period - end date before vaccine date
        invalid_name = ValidValues.valid_name_4_instances[0]
        name_period = obtain_current_name_period(invalid_name["period"], ValidValues.for_occurrenceDateTime)
        self.assertFalse(name_period)

    def test_obtain_current_name_period_(self):
        """Test obtaining current name based on period for both Patient and Practitioner."""

        def run_test_with_name_instances(name_instances):
            """
            Helper function to test name periods for given name instances.
            """
            # Name with vaccine date between current period (start and end)
            valid_name = name_instances[1]
            current_name = obtain_current_name_period(valid_name["period"], ValidValues.for_occurrenceDateTime)
            self.assertTrue(current_name)

            # Name with expired period - end date before vaccine date
            invalid_name = name_instances[0]
            name_period = obtain_current_name_period(invalid_name["period"], ValidValues.for_occurrenceDateTime)
            self.assertFalse(name_period)

            # Two names before and after vaccinedate
            test_names = [
                {
                    **name_instances[1],
                    "period": {"start": ValidValues.for_date_before_vaccinedatetime},
                },
                {
                    **name_instances[0],
                    "period": {"start": ValidValues.for_date_after_vaccinedatetime},
                },
            ]
            occurrence_date = ValidValues.for_occurrenceDateTime
            result = get_current_name_instance(test_names, occurrence_date)
            self.assertEqual(
                result,
                (
                    0,
                    {
                        **name_instances[1],
                        "period": {"start": ValidValues.for_date_before_vaccinedatetime},
                    },
                ),
            )

        run_test_with_name_instances(ValidValues.valid_name_4_instances)
        run_test_with_name_instances(ValidValues.valid_name_4_instances_practitioner)

    def test_patient_and_practitioner_value_and_index(self):
        """Test retrieving name value and index from Patient/Practitioner resources."""

        valid_json_data = deepcopy(self.json_data)

        # single name exists in json
        test_single_name = [
            (valid_json_data, "given", "Patient", ["Sarah"], 0),
            (valid_json_data, "given", "Practitioner", ["Florence"], 0),
            (valid_json_data, "family", "Patient", "Taylor", 0),
            (valid_json_data, "family", "Practitioner", "Nightingale", 0),
        ]

        for imms, name_value, resource_type, expected_name, expected_index in test_single_name:
            name_field, index = patient_and_practitioner_value_and_index(imms, name_value, resource_type)
            self.assertEqual(name_field, expected_name)
            self.assertEqual(index, expected_index)

        updated_valid_json_data = self.updated_PatientandPractitioner_json

        updated_practitioner_names = deepcopy(ValidValues.valid_name_4_instances_practitioner)

        updated_practitioner_names[0], updated_practitioner_names[2] = (
            updated_practitioner_names[2],
            updated_practitioner_names[0],
        )

        updated_valid_json_data["contained"][0]["name"] = updated_practitioner_names

        test_cases = [
            (updated_valid_json_data, "given", "Patient", ["Sarah"], 1),
            (updated_valid_json_data, "given", "Practitioner", ["Florence"], 1),
            (updated_valid_json_data, "family", "Patient", "Taylor", 1),
            (updated_valid_json_data, "family", "Practitioner", "Night", 1),
        ]

        #  Check correct name and index is returned
        for imms, name_value, resource_type, expected_name, expected_index in test_cases:
            name_field, index = patient_and_practitioner_value_and_index(imms, name_value, resource_type)
            self.assertEqual(name_field, expected_name)
            self.assertEqual(index, expected_index)


if __name__ == "__main__":
    unittest.main()
