def remove_personal_info(data):
    if isinstance(data, dict):
        keys_to_remove = ["SiteCode", "SiteName", "LocalPatient", "CareSetting", "IpAddress", "UserId", "UserName", "UserEmail", "Patient", "Practitioner"]
        if "linkId" in data and data["linkId"] in keys_to_remove:
            return None  # Remove the questionnaire answers
        if "resourceType" in data and data["resourceType"] in keys_to_remove:
            return None # Remove patient/practitioner elements
        else:
            result = {}
            for key, value in data.items():
                updated_value = remove_personal_info(value) # Loop back through
                if updated_value is not None:
                    result[key] = updated_value # Update value if not in keys_to_remove
            return result if result else None
    elif isinstance(data, list):
        result = [remove_personal_info(object) for object in data if remove_personal_info(object) is not None] # Call remove_personal_info for each element in the array and build a new list 
        return result if result else None
    else:
        return data
    
def filter_immunization(data):
    filtered_data = {
        "resourceType": data["resourceType"],
        "type": data.get("type"),
        "total": data.get("total"),
        "entry": [entry for entry in data.get("entry", []) if entry.get("resourceType") == "Immunization"]
    }

    # If there's only one 'Immunization' entry, directly assign it as 'entry'
    if len(filtered_data["entry"]) == 1:
        filtered_data["entry"] = filtered_data["entry"][0]

    return filtered_data

# fhir_imms = {
#   "resourceType": "Immunization",
#   "contained": [
#     {
#       "resourceType": "QuestionnaireResponse",
#       "questionnaire": "Questionnaire/1",
#       "status": "completed",
#       "item": [
#         {
#           "linkId": "SiteCode",
#           "answer": [
#             {
#               "valueCoding": {
#                 "system": "snomed",
#                 "code": "M242ND"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "SiteName",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "dummy"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "NhsNumberStatus",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "snomed",
#                 "display": "test description"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "LocalPatient",
#           "answer": [
#             {
#               "valueCoding": {
#                 "system": "https://supplierABC/identifiers/patient",
#                 "code": "ACME-patient123456"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "Consent",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "snomed",
#                 "display": "free text"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "CareSetting",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "1127531000000102",
#                 "display": "SNOMED-CT Term description Community health services (qualifier value)"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "IpAddress",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "1.0.0.0"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "UserId",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "test123"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "UserName",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "test"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "UserEmail",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "test@gmail.com"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "SubmittedTimeStamp",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "2020-12-14T10:08:15"
#               }
#             }
#           ]
#         },
#         {
#           "linkId": "ReduceValidation",
#           "answer": [
#             {
#               "valueCoding": {
#                 "code": "TRUE",
#                 "display": "test"
#               }
#             }
#           ]
#         }
#       ]
#     }
#   ],
#   "extension": [
#     {
#       "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
#       "valueCodeableConcept": {
#         "coding": [
#           {
#             "system": "http://snomed.info/sct",
#             "code": "snomed",
#             "display": "snomed"
#           }
#         ]
#       }
#     },
#     {
#       "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
#       "valueCodeableConcept": {
#         "coding": [
#           {
#             "system": "http://snomed.info/sct",
#             "code": "snomed",
#             "display": "snomed"
#           }
#         ]
#       }
#     }
#   ],
#   "identifier": [
#     {
#       "system": "https://supplierABC/ODSCode",
#       "value": "e045626e-4dc5-4df3-bc35-da25263f901e"
#     }
#   ],
#   "status": "completed",
#   "statusReason": {
#     "coding": [
#       {
#         "system": "http://snomed.info/sct",
#         "code": "snomed",
#         "display": "snomed"
#       }
#     ]
#   },
#   "vaccineCode": {
#     "coding": [
#       {
#         "system": "http://snomed.info/sct",
#         "code": "snomed",
#         "display": "snomed"
#       }
#     ]
#   },
#   "lotNumber": "AAJN11K",
#   "expirationDate": "2020-05-06",
#   "patient": {
#     "identifier": {
#       "system": "https//fhir.nhs.uk/Id/nhs-number",
#       "value": "1234567891"
#     }
#   },
#   "occurrenceDateTime": "2020-12-14T10:08:15+00:00",
#   "primarySource": "true",
#   "location": {
#     "identifier": {
#       "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#       "value": "B0C4P"
#     }
#   },
#   "site": {
#     "coding": [
#       {
#         "system": "http://snomed.info/sct",
#         "code": "LA",
#         "display": "left arm"
#       }
#     ]
#   },
#   "route": {
#     "coding": [
#       {
#         "system": "http://snomed.info/sct",
#         "code": "IM",
#         "display": "injection, intramuscular"
#       }
#     ]
#   },
#   "doseQuantity": {
#     "value": 5,
#     "unit": "mg",
#     "system": "http://unitsofmeasure.org",
#     "code": "snomed"
#   },
#   "protocolApplied": [
#     {
#       "targetDisease": [
#         {
#           "coding": [
#             {
#               "code": "40468003"
#             }
#           ]
#         }
#       ],
#       "doseNumberPositiveInt": 5
#     }
#   ],
#   "reportOrigin": {
#     "text": "sample"
#   },
#   "reasonCode": [
#     {
#       "coding": [
#         {
#           "code": "snomed",
#           "display": "test"
#         }
#       ]
#     }
#   ],
#   "recorded": "2010-05-06",
#   "manufacturer": {
#     "display": "test"
#   },
#   "performer": [
#     {
#       "actor": {
#         "reference": "Practitioner/1",
#         "type": "Practitioner",
#         "identifier": {
#           "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#           "value": "B0C4P"
#         }
#       }
#     }
#   ]
# }

# fhir_bundle = {
#     "resourceType": "Bundle",
#     "type": "searchset",
#     "total": 3,
#     "entry": [
#         {
#             "resourceType": "Immunization",
#             "contained": [
#               {
#                 "resourceType": "QuestionnaireResponse",
#                 "questionnaire": "Questionnaire/1",
#                 "status": "completed",
#                 "item": [
#                   {
#                     "linkId": "SiteCode",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "system": "snomed",
#                           "code": "M242ND"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "SiteName",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "dummy"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "NhsNumberStatus",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "snomed",
#                           "display": "test description"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "LocalPatient",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "system": "https://supplierABC/identifiers/patient",
#                           "code": "ACME-patient123456"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "Consent",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "snomed",
#                           "display": "free text"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "CareSetting",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "1127531000000102",
#                           "display": "SNOMED-CT Term description Community health services (qualifier value)"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "IpAddress",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "1.0.0.0"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "UserId",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "test123"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "UserName",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "test"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "UserEmail",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "test@gmail.com"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "SubmittedTimeStamp",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "2020-12-14T10:08:15"
#                         }
#                       }
#                     ]
#                   },
#                   {
#                     "linkId": "ReduceValidation",
#                     "answer": [
#                       {
#                         "valueCoding": {
#                           "code": "TRUE",
#                           "display": "test"
#                         }
#                       }
#                     ]
#                   }
#                 ]
#               }
#             ],
#             "extension": [
#               {
#                 "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
#                 "valueCodeableConcept": {
#                   "coding": [
#                     {
#                       "system": "http://snomed.info/sct",
#                       "code": "snomed",
#                       "display": "snomed"
#                     }
#                   ]
#                 }
#               },
#               {
#                 "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
#                 "valueCodeableConcept": {
#                   "coding": [
#                     {
#                       "system": "http://snomed.info/sct",
#                       "code": "snomed",
#                       "display": "snomed"
#                     }
#                   ]
#                 }
#               }
#             ],
#             "identifier": [
#               {
#                 "system": "https://supplierABC/ODSCode",
#                 "value": "e045626e-4dc5-4df3-bc35-da25263f901e"
#               }
#             ],
#             "status": "completed",
#             "statusReason": {
#               "coding": [
#                 {
#                   "system": "http://snomed.info/sct",
#                   "code": "snomed",
#                   "display": "snomed"
#                 }
#               ]
#             },
#             "vaccineCode": {
#               "coding": [
#                 {
#                   "system": "http://snomed.info/sct",
#                   "code": "snomed",
#                   "display": "snomed"
#                 }
#               ]
#             },
#             "lotNumber": "AAJN11K",
#             "expirationDate": "2020-05-06",
#             "patient": {
#               "identifier": {
#                 "system": "https//fhir.nhs.uk/Id/nhs-number",
#                 "value": "1234567891"
#               }
#             },
#             "occurrenceDateTime": "2020-12-14T10:08:15+00:00",
#             "primarySource": "true",
#             "location": {
#               "identifier": {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "B0C4P"
#               }
#             },
#             "site": {
#               "coding": [
#                 {
#                   "system": "http://snomed.info/sct",
#                   "code": "LA",
#                   "display": "left arm"
#                 }
#               ]
#             },
#             "route": {
#               "coding": [
#                 {
#                   "system": "http://snomed.info/sct",
#                   "code": "IM",
#                   "display": "injection, intramuscular"
#                 }
#               ]
#             },
#             "doseQuantity": {
#               "value": 5,
#               "unit": "mg",
#               "system": "http://unitsofmeasure.org",
#               "code": "snomed"
#             },
#             "protocolApplied": [
#               {
#                 "targetDisease": [
#                   {
#                     "coding": [
#                       {
#                         "code": "40468003"
#                       }
#                     ]
#                   }
#                 ],
#                 "doseNumberPositiveInt": 5
#               }
#             ],
#             "reportOrigin": {
#               "text": "sample"
#             },
#             "reasonCode": [
#               {
#                 "coding": [
#                   {
#                     "code": "snomed",
#                     "display": "test"
#                   }
#                 ]
#               }
#             ],
#             "recorded": "2010-05-06",
#             "manufacturer": {
#               "display": "test"
#             },
#             "performer": [
#               {
#                 "actor": {
#                   "reference": "Practitioner/1",
#                   "type": "Practitioner",
#                   "identifier": {
#                     "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                     "value": "B0C4P"
#                   }
#                 }
#               }
#             ]
#           },
#         {
#           "resourceType": "Practitioner",
#           "name": [
#             {
#               "family": "test",
#               "given": ["test"]
#             }
#           ],
#           "identifier": [
#             {
#               "system": "http://hl7.org/fhir/sid/us-npi",
#               "value": "1234567890"
#             }
#           ]
#         },
#         {
#           "resourceType": "Patient",
#           "name": [
#             {
#               "family": "test_family_name",
#               "given": ["test_given_name_first", "test_given_name_middle"]
#             }
#           ],
#           "id": "9000000009",
#           "birthDate": "1990-01-01",
#           "gender": "male",
#           "address": [
#             {
#               "postalCode": "HX1 1UN"
#             }
#           ]
#         }  
#     ]
#   }

# filtered_fhir_imms = remove_personal_info(fhir_imms)
# filtered_fhir_bundle = remove_personal_info(fhir_bundle)
# print(filtered_fhir_imms)
# print(" ")
# print(filtered_fhir_bundle)
