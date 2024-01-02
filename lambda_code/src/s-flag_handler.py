def remove_personal_info(data):
    if isinstance(data, dict):
        keys_to_remove = ["SiteCode", "SiteName", "LocalPatient", "CareSetting", "IpAddress", "UserId", "UserName", "UserEmail"]
        if "linkId" in data and data["linkId"] in keys_to_remove:
            return None  # Remove the field from the structure
        else:
            result = {}
            for key, value in data.items():
                updated_value = remove_personal_info(value)
                if updated_value is not None:
                    result[key] = updated_value
            return result
    elif isinstance(data, list):
        result = []
        for item in data:
            updated_item = remove_personal_info(item)
            if updated_item is not None:
                result.append(updated_item)
        return result

fhir_data = {
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
          "linkId": "NhsNumberStatus",
          "answer": [
            {
              "valueCoding": {
                "code": "snomed",
                "display": "test description"
              }
            }
          ]
        },
        {
          "linkId": "LocalPatient",
          "answer": [
            {
              "valueCoding": {
                "system": "https://supplierABC/identifiers/patient",
                "code": "ACME-patient123456"
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
          "linkId": "CareSetting",
          "answer": [
            {
              "valueCoding": {
                "code": "1127531000000102",
                "display": "SNOMED-CT Term description Community health services (qualifier value)"
              }
            }
          ]
        },
        {
          "linkId": "IpAddress",
          "answer": [
            {
              "valueCoding": {
                "code": "1.0.0.0"
              }
            }
          ]
        },
        {
          "linkId": "UserId",
          "answer": [
            {
              "valueCoding": {
                "code": "test123"
              }
            }
          ]
        },
        {
          "linkId": "UserName",
          "answer": [
            {
              "valueCoding": {
                "code": "test"
              }
            }
          ]
        },
        {
          "linkId": "UserEmail",
          "answer": [
            {
              "valueCoding": {
                "code": "test@gmail.com"
              }
            }
          ]
        },
        {
          "linkId": "SubmittedTimeStamp",
          "answer": [
            {
              "valueCoding": {
                "code": "2020-12-14T10:08:15"
              }
            }
          ]
        },
        {
          "linkId": "ReduceValidation",
          "answer": [
            {
              "valueCoding": {
                "code": "TRUE",
                "display": "test"
              }
            }
          ]
        }
      ]
    }
  ],
  "extension": [
    {
      "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
      "valueCodeableConcept": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "snomed",
            "display": "snomed"
          }
        ]
      }
    },
    {
      "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
      "valueCodeableConcept": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "snomed",
            "display": "snomed"
          }
        ]
      }
    }
  ],
  "identifier": [
    {
      "system": "https://supplierABC/ODSCode",
      "value": "e045626e-4dc5-4df3-bc35-da25263f901e"
    }
  ],
  "status": "completed",
  "statusReason": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "snomed",
        "display": "snomed"
      }
    ]
  },
  "vaccineCode": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "snomed",
        "display": "snomed"
      }
    ]
  },
  "lotNumber": "AAJN11K",
  "expirationDate": "2020-05-06",
  "patient": {
    "identifier": {
      "system": "https//fhir.nhs.uk/Id/nhs-number",
      "value": "1234567891"
    }
  },
  "occurrenceDateTime": "2020-12-14T10:08:15+00:00",
  "primarySource": "true",
  "location": {
    "identifier": {
      "system": "https://fhir.nhs.uk/Id/ods-organization-code",
      "value": "B0C4P"
    }
  },
  "site": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "LA",
        "display": "left arm"
      }
    ]
  },
  "route": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "IM",
        "display": "injection, intramuscular"
      }
    ]
  },
  "doseQuantity": {
    "value": 5,
    "unit": "mg",
    "system": "http://unitsofmeasure.org",
    "code": "snomed"
  },
  "protocolApplied": [
    {
      "targetDisease": [
        {
          "coding": [
            {
              "code": "40468003"
            }
          ]
        }
      ],
      "doseNumberPositiveInt": 5
    }
  ],
  "reportOrigin": {
    "text": "sample"
  },
  "reasonCode": [
    {
      "coding": [
        {
          "code": "snomed",
          "display": "test"
        }
      ]
    }
  ],
  "recorded": "2010-05-06",
  "manufacturer": {
    "display": "test"
  },
  "performer": [
    {
      "actor": {
        "reference": "Practitioner/1",
        "type": "Practitioner",
        "identifier": {
          "system": "https://fhir.nhs.uk/Id/ods-organization-code",
          "value": "B0C4P"
        }
      }
    }
  ]
}

filtered_fhir_data = remove_personal_info(fhir_data)
print(filtered_fhir_data)
