import json
import unittest
from unittest.mock import create_autospec
from pds import PdsService
from models.errors import Severity, Code, create_operation_outcome


class TestPdsService(unittest.TestCase):
    def setUp(self):
        self.pds_service = create_autospec(PdsService)

    def test_pds_get_patient_details_by_id(self):
        """Test PdsService get_patient_details method"""
        patient_id = 9693632109
        expected_patient_data = {'dummy_data'}

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
        
        code = Code.invalid

        severity = Severity.error
        diag = "a-diagnostic"
        error_id = "a-id"

        error = create_operation_outcome(resource_id=error_id, severity=severity, code=code, diagnostics=diag).dict()

        #When
        self.pds_service.get_patient_details.return_value = error
        response = self.pds_service.get_patient_details(invalid_patient_id)
        resourceType = response['resourceType']
        
        #Then
        self.assertEqual(self.pds_service.get_patient_details.call_count, 1)
        self.assertEqual(resourceType, "OperationOutcome")
        

if __name__ == '__main__':
    unittest.main()
