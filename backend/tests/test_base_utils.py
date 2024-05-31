"""Tests for the utils in backend/src"""

import unittest
from copy import deepcopy

from src.base_utils.base_utils import remove_questionnaire_items
from .utils.generic_utils import load_json_data


class TestSrcUtils(unittest.TestCase):
    """Tests for src utils functions"""

    def setUp(self):
        """Set up for each test. This runs before every test"""
        self.input_data = {
            "resourceType": "Immunization",
            "contained": [
                {
                    "resourceType": "QuestionnaireResponse",
                    "id": "QR1",
                    "status": "completed",
                    "item": [
                        {"linkId": "Immunisation", "answer": [{"valueReference": {"reference": "#"}}]},
                        {
                            "linkId": "LinkId1",
                            "answer": [{"valueCoding": {"code": "abc", "system": "a_system"}}],
                        },
                        {"linkId": "LinkId2", "answer": [{"valueBoolean": False}]},
                        {
                            "linkId": "LinkId3",
                            "answer": [{"valueReference": {"identifier": {"system": "a_system", "value": "xyz"}}}],
                        },
                        {"linkId": "LinkId4", "answer": [{"valueDateTime": "2021-02-07T13:44:07+00:00"}]},
                        {"linkId": "LinkId5", "answer": [{"valueString": "Specialist Nurse Practitioner"}]},
                    ],
                }
            ],
        }

    def test_remove_questionnaire_items(self):
        """Test that remove_questionnaire_items appropriately removes the requested items"""

        # Questionnaire item contains the link ids to delete
        input_data = deepcopy(self.input_data)

        expected_output = {
            "resourceType": "Immunization",
            "contained": [
                {
                    "resourceType": "QuestionnaireResponse",
                    "id": "QR1",
                    "status": "completed",
                    "item": [
                        {"linkId": "Immunisation", "answer": [{"valueReference": {"reference": "#"}}]},
                        {
                            "linkId": "LinkId1",
                            "answer": [{"valueCoding": {"code": "abc", "system": "a_system"}}],
                        },
                        {"linkId": "LinkId4", "answer": [{"valueDateTime": "2021-02-07T13:44:07+00:00"}]},
                    ],
                }
            ],
        }

        self.assertEqual(remove_questionnaire_items(input_data, ["LinkId2", "LinkId3", "LinkId5"]), expected_output)

        # Questionnaire item does not contain the link id to delete
        input_data = deepcopy(self.input_data)
        self.assertEqual(remove_questionnaire_items(input_data, ["LinkId6"]), self.input_data)

        # Questionnaire exists, but does not contain item
        input_data = {
            "resourceType": "Immunization",
            "contained": [{"resourceType": "QuestionnaireResponse", "id": "QR1", "status": "completed"}],
        }
        expected_output = deepcopy(input_data)
        self.assertEqual(remove_questionnaire_items(input_data, ["LinkId1"]), expected_output)

        # Contained exists, but does not contain questionnaire
        input_data = {"resourceType": "Immunization", "contained": [{"resourceType": "Patient", "id": "Pat1"}]}
        expected_output = deepcopy(input_data)
        self.assertEqual(remove_questionnaire_items(input_data, ["LinkId1"]), expected_output)

        # Contained does not exist
        input_data = {"resourceType": "Immunization"}
        expected_output = deepcopy(input_data)
        self.assertEqual(remove_questionnaire_items(input_data, ["LinkId1"]), expected_output)
