import os
import unittest
from unittest.mock import MagicMock, ANY
import boto3
import json
import botocore.exceptions
from moto import mock_dynamodb
from uuid import uuid4
from models.errors import IdentifierDuplicationError, ResourceNotFoundError, UnhandledResponseError
from fhir_batch_repository import ImmunizationBatchRepository
imms_id = str(uuid4())

@mock_dynamodb
class TestImmunizationBatchRepository(unittest.TestCase):
    
    def setUp(self):
        os.environ["DYNAMODB_TABLE_NAME"] = "test-immunization-table"
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
        self.table = self.dynamodb.create_table(
            TableName=os.environ["DYNAMODB_TABLE_NAME"],
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "IdentifierPK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "IdentifierGSI",
                    "KeySchema": [
                        {"AttributeName": "IdentifierPK", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        
        self.table.wait_until_exists()
        self.repository = ImmunizationBatchRepository()
        self.table.put_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})
        self.table.query = MagicMock(return_value={})
        self.immunization = {
            "id": imms_id,
            "identifier": [{"system": "test-system", "value": "12345"}],
            "contained": [{"resourceType": "Patient", "identifier": [{"value": "98765"}]}],
        }
        self.table.update_item = MagicMock(return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}})

class TestCreateImmunization(TestImmunizationBatchRepository): 
    
    def test_create_immunization(self):
        """it should create Immunization and return imms id location"""

        self.repository.create_immunization(self.immunization , "supplier", "vax-type", self.table, False)
        item = self.table.put_item.call_args.kwargs["Item"]
        self.table.put_item.assert_called_once_with(
            Item={
                    "PK": ANY,
                    "PatientPK": ANY,
                    "PatientSK": ANY,
                    "Resource": json.dumps(self.immunization),
                    "IdentifierPK": ANY,
                    "Operation": "CREATE",
                    "Version": 1,
                    "SupplierSystem": "supplier",
                },
                ConditionExpression=ANY
        )
        self.assertEqual(item["PK"], f'Immunization#{self.immunization ["id"]}')


    def test_create_immunization_duplicate(self):
        """it should not create Immunization since the request is duplicate"""


        self.table.query = MagicMock(return_value={
            "id": imms_id,
            "identifier": [{"system": "test-system", "value": "12345"}],
            "contained": [{"resourceType": "Patient", "identifier": [{"value": "98765"}]}],
            "Count": 1
        })
        with self.assertRaises(IdentifierDuplicationError):
            self.repository.create_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.table.put_item.assert_not_called()  

    def test_create_should_catch_dynamo_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        bad_request = 400
        response = {"ResponseMetadata": {"HTTPStatusCode": bad_request}}
        self.table.put_item = MagicMock(return_value=response)
        with self.assertRaises(UnhandledResponseError) as e:
            self.repository.create_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.assertDictEqual(e.exception.response, response)  


    def test_create_immunization_unhandled_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        response = {'Error': {'Code': 'InternalServerError'}}
        with unittest.mock.patch.object(self.table, 'put_item', side_effect=botocore.exceptions.ClientError({"Error": {"Code": "InternalServerError"}}, "PutItem")):
            with self.assertRaises(UnhandledResponseError) as e:
                self.repository.create_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.assertDictEqual(e.exception.response, response)          


class TestUpdateImmunization(TestImmunizationBatchRepository): 
    def test_update_immunization(self):
        """it should update Immunization record"""

        test_cases = [
            # Update cenario
            {
                "query_response": {
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            },
            # Reinstated scenario
            {
                "query_response": {
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1,
                        "DeletedAt": "20210101"
                    }]
                }
            },
            # update reinstated scenario
            {
                "query_response": {
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1,
                        "DeletedAt": "reinstated"
                    }]
                }
            }
        ] 
        for case in test_cases:
            with self.subTest():
                self.table.query = MagicMock(return_value=case["query_response"])
                response = self.repository.update_immunization(self.immunization, "supplier", "vax-type", self.table, False)
                self.table.update_item.assert_called()
                self.assertEqual(response, f'Immunization#{self.immunization ["id"]}')
  
    def test_update_immunization_not_found(self):
        """it should not update Immunization since the imms id not found"""

        with self.assertRaises(ResourceNotFoundError):
            self.repository.update_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.table.update_item.assert_not_called()

    def test_update_should_catch_dynamo_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        bad_request = 400
        response = {"ResponseMetadata": {"HTTPStatusCode": bad_request}}
        self.table.update_item = MagicMock(return_value=response)
        self.table.query = MagicMock(return_value={
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            )
        with self.assertRaises(UnhandledResponseError) as e:
            self.repository.update_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.assertDictEqual(e.exception.response, response)  

    def test_update_immunization_unhandled_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        response = {'Error': {'Code': 'InternalServerError'}}
        with unittest.mock.patch.object(self.table, 'update_item', side_effect=botocore.exceptions.ClientError({"Error": {"Code": "InternalServerError"}}, "UpdateItem")):
            with self.assertRaises(UnhandledResponseError) as e:
                self.table.query = MagicMock(return_value={
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            )
                self.repository.update_immunization(self.immunization, "supplier", "vax-type", self.table, False)    
        self.assertDictEqual(e.exception.response, response)

    def test_update_immunization_conditionalcheckfailedexception_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        with unittest.mock.patch.object(self.table, 'update_item', side_effect=botocore.exceptions.ClientError({"Error": {"Code": "ConditionalCheckFailedException"}}, "UpdateItem")):
            with self.assertRaises(ResourceNotFoundError) as e:
                self.table.query = MagicMock(return_value={
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            )
                self.repository.update_immunization(self.immunization, "supplier", "vax-type", self.table, False)    
          
class TestDeleteImmunization(TestImmunizationBatchRepository): 
    def test_delete_immunization(self):
        """it should delete Immunization record"""

        self.table.query = MagicMock(return_value={
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            )
        response = self.repository.delete_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.table.update_item.assert_called_once_with(
            Key={"PK": f"Immunization#{imms_id}"},
            UpdateExpression="SET DeletedAt = :timestamp, Operation = :operation, SupplierSystem = :supplier_system",
            ExpressionAttributeValues={":timestamp": ANY, ":operation": "DELETE", ":supplier_system": "supplier"},
            ReturnValues=ANY,
            ConditionExpression=ANY,
        )
        self.assertEqual(response, f'Immunization#{self.immunization ["id"]}')  

    def test_delete_immunization_not_found(self):
        """it should not delete Immunization since the imms id not found"""

        with self.assertRaises(ResourceNotFoundError):
            self.repository.delete_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.table.update_item.assert_not_called()

    def test_delete_should_catch_dynamo_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        bad_request = 400
        response = {"ResponseMetadata": {"HTTPStatusCode": bad_request}}
        self.table.update_item = MagicMock(return_value=response)
        self.table.query = MagicMock(return_value={
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            )
        with self.assertRaises(UnhandledResponseError) as e:
            self.repository.delete_immunization(self.immunization, "supplier", "vax-type", self.table, False)
        self.assertDictEqual(e.exception.response, response)  

    def test_delete_immunization_unhandled_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        response = {'Error': {'Code': 'InternalServerError'}}
        with unittest.mock.patch.object(self.table, 'update_item', side_effect=botocore.exceptions.ClientError({"Error": {"Code": "InternalServerError"}}, "UpdateItem")):
            with self.assertRaises(UnhandledResponseError) as e:
                self.table.query = MagicMock(return_value={
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            )
                self.repository.delete_immunization(self.immunization, "supplier", "vax-type", self.table, False)    
        self.assertDictEqual(e.exception.response, response)

    def test_delete_immunization_conditionalcheckfailedexception_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""

        with unittest.mock.patch.object(self.table, 'update_item', side_effect=botocore.exceptions.ClientError({"Error": {"Code": "ConditionalCheckFailedException"}}, "UpdateItem")):
            with self.assertRaises(ResourceNotFoundError) as e:
                self.table.query = MagicMock(return_value={
                    "Count": 1,
                    "Items": [{
                        "PK": f"Immunization#{imms_id}",
                        "Resource": json.dumps(self.immunization),
                        "Version": 1
                    }]
                }
            )
                self.repository.delete_immunization(self.immunization, "supplier", "vax-type", self.table, False)

if __name__ == "__main__":
    unittest.main()
