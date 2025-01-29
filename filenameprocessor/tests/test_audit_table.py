"""Tests for audit_table functions"""

from unittest import TestCase
from unittest.mock import patch
from boto3 import resource as boto3_resource
from moto import mock_dynamodb
from errors import UnhandledAuditTableError
from clients import REGION_NAME
from tests.utils_for_tests.values_for_tests import MOCK_ENVIRONMENT_DICT

# Some environment variables are evaluated when  constants and upsert_audit_table are imported,
# so environment dictionary must be mocked first
with patch.dict("os.environ", MOCK_ENVIRONMENT_DICT):
    from constants import AuditTableKeys, AUDIT_TABLE_NAME, AUDIT_TABLE_QUEUE_NAME_GSI, AUDIT_TABLE_FILENAME_GSI
    from audit_table import upsert_audit_table


@mock_dynamodb
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestAuditTable(TestCase):
    """Tests for audit table functions"""

    def setUp(self):
        """Set up test values to be used for the tests"""
        self.dynamodb_resource = boto3_resource("dynamodb", region_name=REGION_NAME)
        self.table = self.dynamodb_resource.create_table(
            TableName=AUDIT_TABLE_NAME,
            KeySchema=[
                {"AttributeName": AuditTableKeys.MESSAGE_ID, "KeyType": "HASH"},
                # {"AttributeName": "placeholder", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": AuditTableKeys.MESSAGE_ID, "AttributeType": "S"},
                {"AttributeName": AuditTableKeys.FILENAME, "AttributeType": "S"},
                {"AttributeName": AuditTableKeys.QUEUE_NAME, "AttributeType": "S"},
                {"AttributeName": AuditTableKeys.STATUS, "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            GlobalSecondaryIndexes=[
                {
                    "IndexName": AUDIT_TABLE_FILENAME_GSI,
                    "KeySchema": [{"AttributeName": AuditTableKeys.FILENAME, "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "KEYS_ONLY"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
                {
                    "IndexName": AUDIT_TABLE_QUEUE_NAME_GSI,
                    "KeySchema": [
                        {"AttributeName": AuditTableKeys.QUEUE_NAME, "KeyType": "HASH"},
                        {"AttributeName": AuditTableKeys.STATUS, "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
            ],
        )

        assert self.table.table_status == "ACTIVE"
        assert len(self.table.global_secondary_indexes) == 2
        assert self.table.global_secondary_indexes[0]["IndexName"] == AUDIT_TABLE_FILENAME_GSI
        assert self.table.global_secondary_indexes[1]["IndexName"] == AUDIT_TABLE_QUEUE_NAME_GSI

    def test_upsert_audit_table(self):
        """Test that the upsert_audit_table function works as expected for the following:
        * Unique files: file is added to the audit table, no error is raised
        * Duplicate files (duplicated file name): file is added to the audit table, DuplicateFileError is raised
        * Overwrites (duplicated message_id): file is not added to the audit table, UnhandledAuditTableError is raised
        """
        message_id_1 = "test_id_1"
        message_id_2 = "test_id_2"
        message_id_3 = "test_id_3"
        file_key_1 = "test_file_1.csv"
        file_key_2 = "test_file_2.csv"
        file_key_4 = "test_file_4.csv"
        created_at_formatted_string_1 = "20240101T01000000"
        created_at_formatted_string_2 = "20240101T02000000"
        created_at_formatted_string_3 = "20240101T03000000"
        created_at_formatted_string_4 = "20240101T04000000"

        # Test case 1: file_key_1 should be added to the audit table with status set to "Processing"
        expected_table_item_1 = {
            "message_id": message_id_1,
            "filename": file_key_1,
            "queue_name": "test_queue",
            "status": "Processing",
            "timestamp": created_at_formatted_string_1,
        }

        # Test case 2: file_key_2 should be added to the audit table with status set to "Queued"
        expected_table_item_2 = {
            "message_id": message_id_2,
            "filename": file_key_2,
            "queue_name": "test_queue",
            "status": "Queued",
            "timestamp": created_at_formatted_string_2,
        }

        # Test case 3: file_key_1 should be added to the audit table again,
        # with status set to "Not processed - duplicate"
        expected_table_item_3 = {
            "message_id": message_id_3,
            "filename": file_key_1,
            "queue_name": "test_queue",
            "status": "Not processed - duplicate",
            "timestamp": created_at_formatted_string_3,
        }

        # Test case 4: file_key_4 should not be added to the audit table because the message_id is a duplicate.
        # Note that this scenario should never occur as a new unique message_id is generated for each file upload,
        # even if the file name is a duplicate, but this test is included for safety because default behaviour of
        # dynamodb is to overwrite the existing item if the message_id is the same.
        expected_table_item_4 = {  # This item should not be added to the table
            "message_id": message_id_3,
            "filename": file_key_4,
            "queue_name": "test_queue",
            "status": "Processed",
            "timestamp": created_at_formatted_string_4,
        }

        # Add a file to the audit table
        self.assertTrue(
            upsert_audit_table(
                message_id_1,
                file_key_1,
                created_at_formatted_string_1,
                queue_name="test_queue",
                file_status="Processing",
                is_existing_file=False,
            )
        )
        table_items = self.table.scan()["Items"]
        assert len(table_items) == 1
        assert expected_table_item_1 in table_items

        # Add another file to the audit table
        self.assertFalse(
            upsert_audit_table(
                message_id_2,
                file_key_2,
                created_at_formatted_string_2,
                queue_name="test_queue",
                file_status="Processing",
                is_existing_file=False,
            )
        )
        table_items = self.table.scan()["Items"]
        assert len(table_items) == 2
        assert expected_table_item_1 in table_items
        assert expected_table_item_2 in table_items

        # Attempt to add the file 1 again
        self.assertTrue(
            upsert_audit_table(
                message_id_3,
                file_key_1,
                created_at_formatted_string_3,
                queue_name="test_queue",
                file_status="Not processed - duplicate",
                is_existing_file=False,
            )
        )

        # Check that the file has been added to the audit table again,
        # with the different message_id and created_at_formatted_string
        table_items = self.table.scan()["Items"]
        assert len(table_items) == 3
        assert expected_table_item_1 in table_items
        assert expected_table_item_2 in table_items
        assert expected_table_item_3 in table_items

        # Attempt to add a file that is already in the table with the same message_id
        with self.assertRaises(UnhandledAuditTableError):
            upsert_audit_table(
                message_id_3,
                file_key_4,
                created_at_formatted_string_4,
                queue_name="test_queue",
                file_status="Processing",
                is_existing_file=False,
            )

        # Check that the file has not been added to the audit table
        table_items = self.table.scan()["Items"]
        assert len(table_items) == 3
        assert expected_table_item_1 in table_items
        assert expected_table_item_2 in table_items
        assert expected_table_item_3 in table_items
        assert expected_table_item_4 not in table_items
