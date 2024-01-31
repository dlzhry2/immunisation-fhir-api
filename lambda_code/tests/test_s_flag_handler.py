from s_flag_handler import handle_s_flag

import unittest


class TestRemovePersonalInfo(unittest.TestCase):
    input_immunization = {
        "resourceType": "Immunization",
        "contained": [
            {
                "resourceType": "QuestionnaireResponse",
                "questionnaire": "Questionnaire/1",
                "status": "completed",
                "item": [
                    {
                        "linkId": "SiteCode",
                        "answer": [
                            {
                                "valueCoding": {
                                    "system": "snomed",
                                    "code": "M242ND"
                                }
                            }
                        ]
                    },
                    {
                        "linkId": "SiteName",
                        "answer": [
                            {
                                "valueCoding": {
                                    "code": "dummy"
                                }
                            }
                        ]
                    },
                    {
                        "linkId": "Example",
                        "answer": [
                            {
                                "valueCoding": {
                                    "system": "snomed",
                                    "code": "M242ND"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }

    def test_remove_personal_info(self):
        expected_output = {
            "resourceType": "Immunization",
            "contained": [
                {
                    "resourceType": "QuestionnaireResponse",
                    "questionnaire": "Questionnaire/1",
                    "status": "completed",
                    "item": [
                        {
                            "linkId": "Example",
                            "answer": [
                                {
                                    "valueCoding": {
                                        "system": "snomed",
                                        "code": "M242ND"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        patient = {"meta": {"security": [{"display": "restricted"}]}}

        result = handle_s_flag(self.input_immunization, patient)
        self.assertEqual(result, expected_output)

    def test_when_missing_patient_fields_do_not_remove_personal_info(self):
        expected_output = self.input_immunization

        patient = {"meta": {}}

        result = handle_s_flag(self.input_immunization, patient)
        self.assertEqual(result, expected_output)
