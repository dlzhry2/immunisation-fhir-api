from unittest.mock import ANY

def _create_a_patient(nhs_number):
    return {
        "address": [
            {
                "id": ANY,
                "line": [
                    ANY
                ],
                "period": {
                    "start": ANY
                },
                "postalCode": ANY,
                "use": ANY
            }
        ],
        "birthDate": ANY,
        "gender": ANY,
        "generalPractitioner": [
            {
                "id": ANY,
                "identifier": {
                    "period": {
                        "start": ANY
                    },
                    "system": ANY,
                    "value": ANY
                },
                "type": ANY
            }
        ],
        "id": ANY,
        "identifier": [
            {
                "extension": [
                    {
                        "url": ANY,
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "code": ANY,
                                    "display": ANY,
                                    "system": ANY,
                                    "version": ANY
                                }
                            ]
                        }
                    }
                ],
                "system": ANY,
                "value": nhs_number
            }
        ],
        "meta": {
            "security": [
                {
                    "code": ANY,
                    "display": ANY,
                    "system": ANY
                }
            ],
            "versionId": ANY
        },
        "name": [
            {
                "family": ANY,
                "given": [
                    ANY
                ],
                "id": ANY,
                "period": {
                    "start": ANY
                },
                "prefix": [
                    ANY
                ],
                "use": ANY
            }
        ],
        "resourceType": "Patient"
    }