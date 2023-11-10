import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, ANY

import botocore.exceptions
from boto3.dynamodb.conditions import Attr

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_repository import ImmunisationRepository
from models.errors import ResourceNotFoundError


class TestImmunisationRepository(unittest.TestCase):
    def setUp(self):
        self.table = MagicMock()
        self.repository = ImmunisationRepository(table=self.table)

    @staticmethod
    def _make_id(_id):
        return f"Immunization#{_id}"

    def test_get_immunization_by_id(self):
        """it should find an Immunization by id"""
        imms_id = "an-id"
        resource = {"foo": "bar"}
        self.table.get_item = MagicMock(return_value={"Item": {"Resource": json.dumps(resource)}})

        imms = self.repository.get_immunization_by_id(imms_id)

        self.assertDictEqual(resource, imms)
        self.table.get_item.assert_called_once_with(Key={"PK": self._make_id(imms_id)})

    def test_immunization_not_found(self):
        """it should return None if Immunization doesn't exist"""
        imms_id = "non-existent-id"
        self.table.get_item = MagicMock(return_value={})

        imms = self.repository.get_immunization_by_id(imms_id)
        self.assertIsNone(imms)

    def test_create_immunization(self):
        """it should create Immunization, and return created object"""
        imms_id = "an-id"
        imms = {"id": imms_id}
        self.table.put_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})

        res_imms = self.repository.create_immunization(imms)

        self.assertDictEqual(res_imms, imms)
        self.table.put_item.assert_called_once_with(
            Item={"PK": self._make_id(imms_id),
                  "Resource": json.dumps(imms)})

    def test_create_unsuccessful(self):
        """it should return None if response is non-200"""
        bad_req = 400
        self.table.put_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": bad_req}})

        res_imms = self.repository.create_immunization({"id": "an-id"})

        self.assertIsNone(res_imms)

    def test_delete_immunization(self):
        """it should logical delete Immunization by setting DeletedAt attribute"""
        imms_id = "an-id"
        dynamo_response = {"ResponseMetadata": {"HTTPStatusCode": 200}, "Attributes": {"Resource": {}}}
        self.table.update_item = MagicMock(return_value=dynamo_response)

        now_epoch = 123456
        with patch("time.time") as mock_time:
            mock_time.return_value = now_epoch
            # When
            _id = self.repository.delete_immunization(imms_id)

        # Then
        self.table.update_item.assert_called_once_with(
            Key={"PK": self._make_id(imms_id)},
            UpdateExpression='SET DeletedAt = :timestamp',
            ExpressionAttributeValues={
                ':timestamp': now_epoch,
            },
            ReturnValues=ANY, ConditionExpression=ANY
        )

    def test_delete_returns_old_resource(self):
        """it should return existing Immunization when delete is successful"""

        imms_id = "an-id"
        resource = {"foo": "bar"}
        dynamo_response = {"ResponseMetadata": {"HTTPStatusCode": 200}, "Attributes": {"Resource": resource}}
        self.table.update_item = MagicMock(return_value=dynamo_response)

        now_epoch = 123456
        with patch("time.time") as mock_time:
            mock_time.return_value = now_epoch
            # When
            act_resource = self.repository.delete_immunization(imms_id)

        # Then
        self.table.update_item.assert_called_once_with(
            Key=ANY, UpdateExpression=ANY, ExpressionAttributeValues=ANY, ConditionExpression=ANY,
            ReturnValues="ALL_NEW",
        )
        self.assertDictEqual(act_resource, resource)

    def test_multiple_delete_should_not_update_timestamp(self):
        """when delete is called multiple times, or when it doesn't exist, it should not update DeletedAt,
        and it should return Error"""
        imms_id = "an-id"
        error_res = {"Error": {"Code": "ConditionalCheckFailedException"}}
        self.table.update_item.side_effect = botocore.exceptions.ClientError(
            error_response=error_res,
            operation_name="an-op")

        res = self.repository.delete_immunization(imms_id)

        # Then
        self.table.update_item.assert_called_once_with(
            Key=ANY, UpdateExpression=ANY, ExpressionAttributeValues=ANY, ReturnValues=ANY,
            ConditionExpression=Attr("PK").eq(self._make_id(imms_id)) & Attr("DeletedAt").not_exists()
        )
        self.assertIsInstance(res, ResourceNotFoundError)
        self.assertEqual(res.resource_id, imms_id)
        self.assertEqual(res.resource_type, "Immunization")

    def test_delete_returns_none_when_imms_not_found(self):
        """it should return None if Immunization doesn't exist"""
        imms_id = "a-non-existent-id"
        not_found = 404
        self.table.update_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": not_found}})

        _id = self.repository.delete_immunization(imms_id)

        self.assertIsNone(_id)
