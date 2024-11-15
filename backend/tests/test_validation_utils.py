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

    def test_get_current_name_instance_multiple_names(self):
        """Tests a multiple name occurrences"""

        # Removes use from valid_name_4_instances
        updated_instances = [
            {key: value for key, value in entry.items() if key != "use"} for entry in ValidValues.valid_name_4_instances
        ]

        test_cases = [
            # Test single name instance
            (
                [ValidValues.valid_name_4_instances[2]],
                ValidValues.occurrenceDateTime,
                0,
                ValidValues.valid_name_4_instances[2],
            ),
            # Test multiple name instances
            (
                ValidValues.valid_name_4_instances,
                ValidValues.occurrenceDateTime,
                1,
                ValidValues.valid_name_4_instances[1],
            ),
            # Tests when no "use" or period exists
            (
                [ValidValues.valid_name_4_instances[2], ValidValues.valid_name_4_instances[3]],
                ValidValues.occurrenceDateTime,
                0,
                ValidValues.valid_name_4_instances[2],
            ),
            # Tests where "use" is not given, but has period
            (updated_instances, ValidValues.occurrenceDateTime, 1, updated_instances[1]),
            # Test 2 invalid names instances
            (
                [InvalidValues.name_with_missing_values[0], InvalidValues.name_with_missing_values[1]],
                ValidValues.occurrenceDateTime,
                0,
                InvalidValues.name_with_missing_values[0],
            ),
        ]
        for name_value, occurrence_date, expected_index, expected_name in test_cases:
            result = get_current_name_instance(name_value, occurrence_date)
            self.assertEqual(result, (expected_index, expected_name))

    def test_obtain_current_name_period(self):
        """Test obtaining current name based on period for both Patient and Practitioner."""

        def test_name_period_instances(name_instances):
            """
            Helper function to test name periods for given name instances.
            """
            # Tests instance with vaccine date between current period (start and end)
            valid_name = name_instances[1]
            current_period = obtain_current_name_period(valid_name["period"], ValidValues.occurrenceDateTime)
            self.assertTrue(current_period)

            # Tests instance with expired period - end date before vaccine date
            invalid_name = name_instances[0]
            current_period = obtain_current_name_period(invalid_name["period"], ValidValues.occurrenceDateTime)
            self.assertFalse(current_period)

            # Two names one before and one after vaccinedate
            test_names = [
                {
                    **name_instances[1],
                    "period": {"start": ValidValues.date_before_occurenceDateTime},
                },
                {
                    **name_instances[0],
                    "period": {"start": ValidValues.date_after_occurenceDateatetime},
                },
            ]
            occurrence_date = ValidValues.occurrenceDateTime
            result = get_current_name_instance(test_names, occurrence_date)
            self.assertEqual(
                result,
                (
                    0,
                    {
                        **name_instances[1],
                        "period": {"start": ValidValues.date_before_occurenceDateTime},
                    },
                ),
            )

        test_name_period_instances(ValidValues.valid_name_4_instances)
        test_name_period_instances(ValidValues.valid_name_4_instances_practitioner)

    def test_patient_and_practitioner_value_and_index(self):
        """Test retrieving name value and index from Patient/Practitioner resources."""

        # Json data to input
        valid_json_data = deepcopy(self.json_data)
        updated_valid_json_data = self.updated_PatientandPractitioner_json
        invalid_json_data = deepcopy(self.json_data)

        # Amend test data to move valid data in another index position for test purposes
        updated_practitioner_names = deepcopy(ValidValues.valid_name_4_instances_practitioner)
        updated_patient_names = deepcopy(ValidValues.valid_name_4_instances)

        updated_practitioner_names[0], updated_practitioner_names[2] = (
            updated_practitioner_names[2],
            updated_practitioner_names[0],
        )
        updated_patient_names[1], updated_patient_names[3] = (
            updated_patient_names[3],
            updated_patient_names[1],
        )

        updated_valid_json_data["contained"][0]["name"] = updated_practitioner_names
        updated_valid_json_data["contained"][1]["name"] = updated_patient_names

        # Set up invalid data
        invalid_json_data["contained"][0]["name"] = InvalidValues.name_with_missing_values_practitioner
        invalid_json_data["contained"][1]["name"] = InvalidValues.name_with_missing_values

        test_cases = [
            # Test for when single patient and practitioner names
            (valid_json_data, "given", "Patient", ["Sarah"], 0),
            (valid_json_data, "family", "Patient", "Taylor", 0),
            (valid_json_data, "given", "Practitioner", ["Florence"], 0),
            (valid_json_data, "family", "Practitioner", "Nightingale", 0),
            # Tests for when there are multiple patient and practitioner names
            (updated_valid_json_data, "given", "Patient", ["Sarah"], 3),
            (updated_valid_json_data, "family", "Patient", "Taylor", 3),
            (updated_valid_json_data, "given", "Practitioner", ["Florence"], 1),
            (updated_valid_json_data, "family", "Practitioner", "Night", 1),
            # Testing invalid values returns the name value with family and given from list (3rd index)
            (invalid_json_data, "given", "Patient", "", 3),
            (invalid_json_data, "family", "Patient", "Taylor", 3),
            (invalid_json_data, "given", "Practitioner", "", 3),
            (invalid_json_data, "family", "Practitioner", "Nightingale", 3),
        ]

        for imms, name_value, resource_type, expected_name, expected_index in test_cases:
            name_field, index = patient_and_practitioner_value_and_index(imms, name_value, resource_type)
            self.assertEqual(name_field, expected_name)
            self.assertEqual(index, expected_index)

    def test_obtain_name_field_location(self):
        valid_json_data = self.updated_PatientandPractitioner_json
        valid_json_data_single = self.json_data

        test_cases = [
            # Test for the location returned when multiple patient and practitioner names
            (valid_json_data, "given", "Patient", "contained[?(@.resourceType=='Patient')].name[1].given"),
            (valid_json_data, "family", "Patient", "contained[?(@.resourceType=='Patient')].name[1].family"),
            (valid_json_data, "given", "Practitioner", "contained[?(@.resourceType=='Practitioner')].name[1].given"),
            (valid_json_data, "family", "Practitioner", "contained[?(@.resourceType=='Practitioner')].name[1].family"),
            # Test when only one name
            (valid_json_data_single, "given", "Patient", "contained[?(@.resourceType=='Patient')].name[0].given"),
            (valid_json_data_single, "family", "Patient", "contained[?(@.resourceType=='Patient')].name[0].family"),
            (
                valid_json_data_single,
                "given",
                "Practitioner",
                "contained[?(@.resourceType=='Practitioner')].name[0].given",
            ),
            (
                valid_json_data_single,
                "family",
                "Practitioner",
                "contained[?(@.resourceType=='Practitioner')].name[0].family",
            ),
        ]

        for imms, name_value, resource_type, expected_location in test_cases:
            result = obtain_name_field_location(imms, resource_type, name_value)
            self.assertEqual(result, expected_location)


if __name__ == "__main__":
    unittest.main()
