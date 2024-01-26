import os
import sys
import unittest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from s_flag_handler import remove_personal_info

import unittest


class TestRemovePersonalInfo(unittest.TestCase):
    def test_remove_personal_info(self):
        input_data = {
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

        result = remove_personal_info(input_data)
        self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main()
