import json
import unittest
from unittest.mock import create_autospec
from pds import PdsService


class TestPdsService(unittest.TestCase):
    def setUp(self):
        self.pds_service = create_autospec(PdsService)

    def test_pds_get_patient_details_by_id(self):
        """Test PdsService get_patient_details method"""
        patient_id = 9693632109
        expected_patient_data = {'address': [{'id': 'drSwB', 'line': ['1 MOUNT AVENUE', 'BARTON-UPON-HUMBER', 'S HUMBERSIDE'], 'period': {'start': '2001-04-25'}, 'postalCode': 'DN18 5DW', 'use': 'home'}], 'birthDate': '1946-06-23', 'gender': 'male', 'generalPractitioner': [{'id': 'uMbZF', 'identifier': {'period': {'start': '2005-03-05'}, 'system': 'https://fhir.nhs.uk/Id/ods-organization-code', 'value': 'A20047'}, 'type': 'Organization'}], 'id': '9693632109', 'identifier': [{'extension': [{'url': 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus', 'valueCodeableConcept': {'coding': [{'code': '01', 'display': 'Number present and verified', 'system': 'https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatus', 'version': '1.0.0'}]}}], 'system': 'https://fhir.nhs.uk/Id/nhs-number', 'value': '9693632109'}], 'meta': {'security': [{'code': 'U', 'display': 'unrestricted', 'system': 'http://terminology.hl7.org/CodeSystem/v3-Confidentiality'}], 'versionId': '1'}, 'name': [{'family': 'GARTON', 'given': ['Bill'], 'id': 'oHCsm', 'period': {'start': '1977-06-26'}, 'prefix': ['MR'], 'use': 'usual'}], 'resourceType': 'Patient'}

        #When
        self.pds_service.get_patient_details.return_value = {"statusCode": 200,  "body": expected_patient_data}
        response = self.pds_service.get_patient_details(patient_id)

        #Then
        self.pds_service.get_patient_details.assert_called_once_with(patient_id)
        self.assertEqual(response["statusCode"], 200)
        body = response["body"]
        self.assertEqual(body, expected_patient_data)

    def test_validate_patient(self):
        """It should validate lambda's patient id"""
        invalid_patient_id = "invalid_id"

        #When
        self.pds_service.get_patient_details.return_value = {
    "issue": [
        {
            "code": "value",
            "details": {
                "coding": [
                    {
                        "code": "INVALID_RESOURCE_ID",
                        "display": "Resource Id is invalid",
                        "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                        "version": "1"
                    }
                ]
            },
            "severity": "error"
        }
    ],
    "resourceType": "OperationOutcome"
}
        response = self.pds_service.get_patient_details(invalid_patient_id)
        resourceType = response['resourceType']
        
        #Then
        self.assertEqual(self.pds_service.get_patient_details.call_count, 1)
        self.assertEqual(resourceType, "OperationOutcome")
        

if __name__ == '__main__':
    unittest.main()
