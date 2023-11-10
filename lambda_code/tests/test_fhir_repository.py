import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, ANY

import botocore.exceptions
from boto3.dynamodb.conditions import Attr

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_repository import ImmunisationRepository


class TestImmunisationRepository(unittest.TestCase):
    def setUp(self):
        self.table = MagicMock()
        self.repository = ImmunisationRepository(table=self.table)

    def test_get_immunisation_by_id(self):
        """it should find an Immunization by id"""
        imms_id = "an-id"
        resource = {"foo": "bar"}
        self.table.get_item = MagicMock(return_value={"Item": {"Resource": json.dumps(resource)}})
        res_id = f"Immunization#{imms_id}"

        imms = self.repository.get_immunisation_by_id(imms_id)

        self.assertDictEqual(resource, imms)
        self.table.get_item.assert_called_once_with(Key={"PK": res_id})

    def test_immunisation_not_found(self):
        """it should return None if Immunization doesn't exist"""
        imms_id = "non-existent-id"
        self.table.get_item = MagicMock(return_value={})

        imms = self.repository.get_immunisation_by_id(imms_id)
        self.assertIsNone(imms)

    def test_delete_immunisation(self):
        """it should return passed id if logical delete is successful"""
        imms_id = "an-id"
        self.table.update_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})
        res_id = f"Immunization#{imms_id}"

        now_epoch = 123456
        with patch("time.time") as mock_time:
            mock_time.return_value = now_epoch

            # When
            _id = self.repository.delete_immunisation(imms_id)

        # Then
        self.table.update_item.assert_called_once_with(
            Key={"PK": res_id},
            UpdateExpression='SET DeletedAt = :timestamp',
            ExpressionAttributeValues={
                ':timestamp': now_epoch,
            },
            ConditionExpression=ANY
        )
        self.assertEqual(_id, imms_id)

    def test_multiple_delete_should_not_update_timestamp(self):
        """when delete is called multiple times, it should not update DeletedAt"""
        imms_id = "an-id"
        error_res = {"Error": {"Code": "ConditionalCheckFailedException"}}
        self.table.update_item.side_effect = botocore.exceptions.ClientError(
            error_response=error_res,
            operation_name="an-op")

        # When
        _id = self.repository.delete_immunisation(imms_id)

        # Then
        self.table.update_item.assert_called_once_with(
            Key=ANY,
            UpdateExpression=ANY,
            ExpressionAttributeValues=ANY,
            ConditionExpression=Attr("DeletedAt").not_exists()
        )
        self.assertIsNone(_id)

    def test_delete_returns_none_when_imms_not_found(self):
        """it should return None if Immunization doesn't exist"""
        imms_id = "a-non-existent-id"
        not_found = 404
        self.table.update_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": not_found}})

        _id = self.repository.delete_immunisation(imms_id)

        self.assertIsNone(_id)
