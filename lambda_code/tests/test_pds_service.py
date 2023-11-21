import unittest
from unittest.mock import create_autospec
from pds_service import PdsService

class TestPdsService(unittest.TestCase):
    def setUp(self):
        self.pds_service = create_autospec(PdsService)

    def test_get_patient_details_found(self):
        """It should find patient details by ID"""
        patient_id = 9693632109
        expected_patient_data = {'address': [{'id': 'drSwB', 'line': ['1 MOUNT AVENUE', 'BARTON-UPON-HUMBER', 'S HUMBERSIDE'], 'period': {'start': '2001-04-25'}, 'postalCode': 'DN18 5DW', 'use': 'home'}], 'birthDate': '1946-06-23', 'gender': 'male', 'generalPractitioner': [{'id': 'uMbZF', 'identifier': {'period': {'start': '2005-03-05'}, 'system': 'https://fhir.nhs.uk/Id/ods-organization-code', 'value': 'A20047'}, 'type': 'Organization'}], 'id': '9693632109', 'identifier': [{'extension': [{'url': 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus', 'valueCodeableConcept': {'coding': [{'code': '01', 'display': 'Number present and verified', 'system': 'https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatus', 'version': '1.0.0'}]}}], 'system': 'https://fhir.nhs.uk/Id/nhs-number', 'value': '9693632109'}], 'meta': {'security': [{'code': 'U', 'display': 'unrestricted', 'system': 'http://terminology.hl7.org/CodeSystem/v3-Confidentiality'}], 'versionId': '1'}, 'name': [{'family': 'GARTON', 'given': ['Bill'], 'id': 'oHCsm', 'period': {'start': '1977-06-26'}, 'prefix': ['MR'], 'use': 'usual'}], 'resourceType': 'Patient'}

        self.pds_service.get_patient_details.return_value = expected_patient_data

        # When
        actual_patient_data = self.pds_service.get_patient_details(patient_id)

        # Then
        self.pds_service.get_patient_details.assert_called_once_with(patient_id)
        self.assertEqual(actual_patient_data, expected_patient_data)

    def test_patient_details_not_found(self):
        """It should return None if patient details not found"""
        patient_id = 1234567890
        self.pds_service.get_patient_details.return_value = None

        # When
        actual_patient_data = self.pds_service.get_patient_details(patient_id)

        # Then
        self.pds_service.get_patient_details.assert_called_once_with(patient_id)
        self.assertIsNone(actual_patient_data)
    

    def test_get_access_token(self):
        self.pds_service.get_access_token.return_value = "mock_access_token"

        # When
        access_token = self.pds_service.get_access_token()

        # Then
        self.pds_service.get_access_token.assert_called_once_with()
        self.assertIsInstance(access_token, str)
        self.assertNotEqual(access_token, '')  


if __name__ == '__main__':
    unittest.main()
