"""Tests for audit_table functions"""

from unittest import TestCase
from unittest.mock import patch
from boto3 import resource as boto3_resource
from moto import mock_dynamodb

from audit_table import add_to_audit_table
from tests.utils_for_tests.values_for_tests import MOCK_ENVIRONMENT_DICT, STATIC_DATETIME_FORMATTED


@mock_dynamodb
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestAuditTable(TestCase):
    """Tests for audit table functions"""

    def setUp(self):
        """Set up test values to be used for the tests"""
        self.dynamodb_resource = boto3_resource("dynamodb", region_name="eu-west-2")
        self.audit_table_name = MOCK_ENVIRONMENT_DICT["AUDIT_TABLE_NAME"]

        self.table = self.dynamodb_resource.create_table(
            TableName=self.audit_table_name,
            KeySchema=[{"AttributeName": "message_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "message_id", "AttributeType": "S"},
                {"AttributeName": "filename", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "filename_index",
                    "KeySchema": [{"AttributeName": "filename", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "KEYS_ONLY"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
        )

        # # Wait for the table to be active
        # self.table.wait_until_exists()

        assert self.table.table_status == "ACTIVE"
        assert len(self.table.global_secondary_indexes) == 1
        assert self.table.global_secondary_indexes[0]["IndexName"] == "filename_index"

    def test_add_to_audit_table(self):
        """Test that the add_to_audit_table function works as expected"""
        # Add a file to the audit table
        message_id_1 = "test_id_1"
        message_id_2 = "test_id_2"
        message_id_3 = "test_id_3"
        file_key_1 = "test_file_1.csv"
        file_key_2 = "test_file_2.csv"
        created_at_formatted_string_1 = "20240101T01000000"
        created_at_formatted_string_2 = "20240101T02000000"
        created_at_formatted_string_3 = "20240101T03000000"

        expected_table_item_1 = {
            "message_id": message_id_1,
            "filename": file_key_1,
            "status": "Processed",
            "timestamp": created_at_formatted_string_1,
        }

        expected_table_item_2 = {
            "message_id": message_id_2,
            "filename": file_key_2,
            "status": "Processed",
            "timestamp": created_at_formatted_string_2,
        }

        expected_table_item_3 = {
            "message_id": message_id_3,
            "filename": file_key_1,
            "status": "Processed",
            "timestamp": created_at_formatted_string_3,
        }

        # Add a file to the audit table
        assert add_to_audit_table(message_id_1, file_key_1, created_at_formatted_string_1) is True
        table_items = self.table.scan()["Items"]
        assert len(table_items) == 1
        assert expected_table_item_1 in table_items

        # Add another file to the audit table
        assert add_to_audit_table(message_id_2, file_key_2, created_at_formatted_string_2) is True
        table_items = self.table.scan()["Items"]
        assert len(table_items) == 2
        assert expected_table_item_1 in table_items
        assert expected_table_item_2 in table_items

        # Attempt to add the file 1 again - should return FALSE due to the file already being in the table
        assert add_to_audit_table(message_id_3, file_key_1, created_at_formatted_string_3) is False

        # Check that the file has been added to the audit table again,
        # with the different message_id and created_at_formatted_string
        table_items = self.table.scan()["Items"]
        assert len(table_items) == 3
        assert expected_table_item_1 in table_items
        assert expected_table_item_2 in table_items
        assert expected_table_item_3 in table_items
