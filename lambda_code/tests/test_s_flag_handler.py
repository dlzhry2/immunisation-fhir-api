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
                        "linkId": "Consent",
                        "answer": [
                            {
                                "valueCoding": {
                                    "code": "snomed",
                                    "display": "free text"
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
        ],
        "performer": [
            {
                "actor": {
                    "reference": "Practitioner/1",
                    "type": "Practitioner",
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/some-system",
                        "value": "B0C4P"
                    }
                }
            },
            {
                "actor": {
                    "reference": "Organization/1",
                    "type": "Organization",
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/some-system",
                        "value": "B0C4P"
                    }
                }
            }
        ],
        "reportOrigin": {
            "text": "sample"
        },
        "location": {
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "B0C4P"
            }
        }
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
                            "linkId": "SiteCode",
                            "answer": [
                                {
                                    "valueCoding": {
                                        "system": "snomed",
                                        "code": "N2N9I"
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
            ],
            "performer": [
                {
                    "actor": {
                        "reference": "Practitioner/1",
                        "type": "Practitioner",
                        "identifier": {
                            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                            "value": "N2N9I"
                        }
                    }
                },
                {
                    "actor": {
                        "reference": "Organization/1",
                        "type": "Organization",
                        "identifier": {
                            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                            "value": "N2N9I"
                        }
                    }
                }
            ],
        }

        patient = {"meta": {"security": [{"display": "restricted"}]}}

        result = handle_s_flag(self.input_immunization, patient)
        self.assertEqual(result, expected_output)

    def test_when_missing_patient_fields_do_not_remove_personal_info(self):
        expected_output = self.input_immunization

        patient = {"meta": {}}

        result = handle_s_flag(self.input_immunization, patient)
        self.assertEqual(result, expected_output)
