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

    def test_patient_and_practitioner_value_and_index(self):
        """Test retrieving name value and index from Patient/Practitioner resources."""

        imms = deepcopy(self.json_data)
        # Test patient name (given field)
        name_field, index = patient_and_practitioner_value_and_index(imms, "given", "Patient")
        self.assertEqual(name_field, ["Sarah"])
        self.assertEqual(index, 0)

        # Test practitioner name (given field)
        name_field, index = patient_and_practitioner_value_and_index(imms, "given", "Practitioner")
        self.assertEqual(name_field, ["Florence"])
        self.assertEqual(index, 0)

        # TODO  Update to loop for patient, practitioner, given and family
        print(self.updated_PatientandPractitioner_json)

        name_field, index = patient_and_practitioner_value_and_index(
            self.updated_PatientandPractitioner_json, "given", "Patient"
        )
        self.assertEqual(name_field, ["Sarah"])
        self.assertEqual(index, 0)


if __name__ == "__main__":
    unittest.main()
