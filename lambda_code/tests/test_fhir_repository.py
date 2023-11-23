import json
import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch, ANY

import botocore.exceptions
from boto3.dynamodb.conditions import Attr

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_repository import ImmunisationRepository
from models.errors import ResourceNotFoundError, UnhandledResponseError


def _make_id(_id):
    return f"Immunization#{_id}"


class TestGetImmunization(unittest.TestCase):
    def setUp(self):
        self.table = MagicMock()
        self.repository = ImmunisationRepository(table=self.table)

    def test_get_immunization_by_id(self):
        """it should find an Immunization by id"""
        imms_id = "an-id"
        resource = {"foo": "bar"}
        self.table.get_item = MagicMock(return_value={"Item": {"Resource": json.dumps(resource)}})

        imms = self.repository.get_immunization_by_id(imms_id)

        self.assertDictEqual(resource, imms)
        self.table.get_item.assert_called_once_with(Key={"PK": _make_id(imms_id)})

    def test_immunization_not_found(self):
        """it should return None if Immunization doesn't exist"""
        imms_id = "non-existent-id"
        self.table.get_item = MagicMock(return_value={})

        imms = self.repository.get_immunization_by_id(imms_id)
        self.assertIsNone(imms)


class TestCreateImmunization(unittest.TestCase):
    def setUp(self):
        self.table = MagicMock()
        self.repository = ImmunisationRepository(table=self.table)

    def test_create_immunization(self):
        """it should create Immunization, and return created object"""
        imms_id = "an-id"
        imms = {"id": imms_id}
        self.table.put_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})

        res_imms = self.repository.create_immunization(imms)

        self.assertDictEqual(res_imms, imms)
        self.table.put_item.assert_called_once_with(
            Item={"PK": ANY,
                  "Resource": json.dumps(imms)})

    def test_create_immunization_makes_new_id(self):
        """create should create new Logical ID even if one is already provided"""
        imms_id = "original-id-from-request"
        imms = {"id": imms_id}
        self.table.put_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})

        _ = self.repository.create_immunization(imms)

        item = self.table.put_item.call_args.kwargs["Item"]
        self.assertTrue(item["PK"].startswith("Immunization#"))
        self.assertNotEqual(item["PK"], "Immunization#original-id-from-request")

    def test_create_immunization_returns_new_id(self):
        """create should return the persisted object i.e. with new id"""
        imms_id = "original-id-from-request"
        self.table.put_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})

        response = self.repository.create_immunization({"id": imms_id})

        self.assertNotEqual(response["id"], imms_id)

    def test_create_should_catch_dynamo_error(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""
        bad_request = 400
        response = {"ResponseMetadata": {"HTTPStatusCode": bad_request}}
        self.table.put_item = MagicMock(return_value=response)

        with self.assertRaises(UnhandledResponseError) as e:
            # When
            self.repository.create_immunization({"id": "an-id"})

        # Then
        self.assertDictEqual(e.exception.response, response)


class TestDeleteImmunization(unittest.TestCase):
    def setUp(self):
        self.table = MagicMock()
        self.repository = ImmunisationRepository(table=self.table)

    def test_get_deleted_immunization(self):
        """it should return None if Immunization is logically deleted"""
        imms_id = "a-deleted-id"
        self.table.get_item = MagicMock(return_value={"Item": {"Resource": "{}", "DeletedAt": time.time()}})

        imms = self.repository.get_immunization_by_id(imms_id)
        self.assertIsNone(imms)

    def test_delete_immunization(self):
        """it should logical delete Immunization by setting DeletedAt attribute"""
        imms_id = "an-id"
        dynamo_response = {"ResponseMetadata": {"HTTPStatusCode": 200}, "Attributes": {"Resource": "{}"}}
        self.table.update_item = MagicMock(return_value=dynamo_response)

        now_epoch = 123456
        with patch("time.time") as mock_time:
            mock_time.return_value = now_epoch
            # When
            _id = self.repository.delete_immunization(imms_id)

        # Then
        self.table.update_item.assert_called_once_with(
            Key={"PK": _make_id(imms_id)},
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
        dynamo_response = {"ResponseMetadata": {"HTTPStatusCode": 200},
                           "Attributes": {"Resource": json.dumps(resource)}}
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

        with self.assertRaises(ResourceNotFoundError) as e:
            self.repository.delete_immunization(imms_id)

        # Then
        self.table.update_item.assert_called_once_with(
            Key=ANY, UpdateExpression=ANY, ExpressionAttributeValues=ANY, ReturnValues=ANY,
            ConditionExpression=Attr("PK").eq(_make_id(imms_id)) & Attr("DeletedAt").not_exists()
        )

        self.assertIsInstance(e.exception, ResourceNotFoundError)
        self.assertEqual(e.exception.resource_id, imms_id)
        self.assertEqual(e.exception.resource_type, "Immunization")

    def test_delete_throws_error_when_response_can_not_be_handled(self):
        """it should throw UnhandledResponse when the response from dynamodb can't be handled"""
        imms_id = "an-id"
        bad_request = 400
        response = {"ResponseMetadata": {"HTTPStatusCode": bad_request}}
        self.table.update_item = MagicMock(return_value=response)

        with self.assertRaises(UnhandledResponseError) as e:
            # When
            self.repository.delete_immunization(imms_id)

        # Then
        self.assertDictEqual(e.exception.response, response)
