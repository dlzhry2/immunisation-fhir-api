"""Tests for audit_table functions"""

from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy
import json
from boto3 import client as boto3_client
from moto import mock_dynamodb

from tests.utils_for_tests.mock_environment_variables import MOCK_ENVIRONMENT_DICT
from tests.utils_for_tests.generic_setup_and_teardown import GenericSetUp, GenericTearDown
from tests.utils_for_tests.values_for_tests import MockFileDetails, MockAuditTableEntry, AuditTableEntry

# Ensure environment variables are mocked before importing from src files
with patch.dict("os.environ", MOCK_ENVIRONMENT_DICT):
    from constants import AUDIT_TABLE_NAME, AuditTableKeys, FileStatus
    from audit_table import upsert_audit_table, ensure_file_is_not_a_duplicate, get_next_queued_file_details
    from errors import UnhandledAuditTableError, DuplicateFileError
    from clients import REGION_NAME

dynamodb_client = boto3_client("dynamodb", region_name=REGION_NAME)

FILE_DETAILS = MockFileDetails.rsv_ravs


@mock_dynamodb
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestAuditTable(TestCase):
    """Tests for audit table functions"""

    def setUp(self):
        """Set up test values to be used for the tests"""
        GenericSetUp(dynamodb_client=dynamodb_client)

    def tearDown(self):
        """Tear down the test values"""
        GenericTearDown(dynamodb_client=dynamodb_client)

    @staticmethod
    def get_table_items():
        """Return all items in the audit table"""
        return dynamodb_client.scan(TableName=AUDIT_TABLE_NAME).get("Items", [])

    @staticmethod
    def add_entry_to_table(entry: MockAuditTableEntry):
        """Add an entry to the audit table"""
        dynamodb_client.put_item(
            TableName=AUDIT_TABLE_NAME, Item={k: {"S": v} for k, v in entry.audit_table_entry.items()}
        )

    def assert_table_entry(self, file_details: AuditTableEntry, expected_status: FileStatus):
        """Assert that the file details are in the audit table"""
        table_entry = dynamodb_client.get_item(
            TableName=AUDIT_TABLE_NAME, Key={AuditTableKeys.MESSAGE_ID: {"S": file_details.message_id}}
        ).get("Item")
        expected_audit_table_entry = {**file_details.audit_table_entry, "status": expected_status}
        self.assertEqual(table_entry, {k: {"S": v} for k, v in expected_audit_table_entry.items()})

    def test_get_next_queued_file_details(self):
        """Test that the get_next_queued_file_details function returns the correct file details"""
        # NOTE: Throughout this test the assertions will be checking for the next queued RAVS_RSV file.
        queue_to_check = "RAVS_RSV"

        # Test case 1: no files in audit table
        self.assertIsNone(get_next_queued_file_details(queue_to_check))

        # Test case 2: files in audit table, but none of the files are in the RAVS_RSV queue
        self.add_entry_to_table(MockAuditTableEntry.emis_flu_1_queued)  # different queue
        self.add_entry_to_table(MockAuditTableEntry.emis_rsv_1_queued)  # different queue
        self.add_entry_to_table(MockAuditTableEntry.ravs_flu_1_queued)  # different queue
        self.add_entry_to_table(MockAuditTableEntry.ravs_rsv_1_processed)  # same queue but already processed
        self.assertIsNone(get_next_queued_file_details(queue_to_check))

        # Test case 3: one queued file in the ravs_rsv queue
        self.add_entry_to_table(MockAuditTableEntry.ravs_rsv_2_queued)
        self.assertEqual(
            get_next_queued_file_details(queue_to_check), MockAuditTableEntry.ravs_rsv_2_queued.audit_table_entry
        )

        # Test case 4: multiple queued files in the RAVS_RSV queue
        # Note that ravs_rsv files 3 and 4 have later timestamps than file 2, so file 2 remains the first in the queue
        self.add_entry_to_table(MockAuditTableEntry.ravs_rsv_3_queued)
        self.add_entry_to_table(MockAuditTableEntry.ravs_rsv_4_queued)
        self.assertEqual(
            get_next_queued_file_details(queue_to_check), MockAuditTableEntry.ravs_rsv_2_queued.audit_table_entry
        )

    def test_ensure_file_is_not_a_duplicate(self):
        """
        Tests that ensure_file_is_not_a_duplicate raises a DuplicateFile Error if and only if the file is a
        duplicate in the audit table.
        """
        # Test case 1: file is not a duplicate (and so is not currently in the audit table)
        self.assertIsNone(
            ensure_file_is_not_a_duplicate(FILE_DETAILS.file_key, FILE_DETAILS.created_at_formatted_string)
        )

        # Add the file to the audit table
        dynamodb_client.put_item(
            TableName=AUDIT_TABLE_NAME,
            Item={
                AuditTableKeys.MESSAGE_ID: {"S": FILE_DETAILS.message_id},
                AuditTableKeys.FILENAME: {"S": FILE_DETAILS.file_key},
                AuditTableKeys.TIMESTAMP: {"S": FILE_DETAILS.created_at_formatted_string},
            },
        )

        # Test case 2: file is a duplicate (duplicate file_key, unique creation time)
        with self.assertRaises(DuplicateFileError):
            ensure_file_is_not_a_duplicate(
                FILE_DETAILS.file_key, FILE_DETAILS.created_at_formatted_string.replace("2024", "2025")
            )

    def test_upsert_audit_table_2(self):
        """Test that the upsert_audit_table function works as expected for the following:
        * Unique files: file is added to the audit table, no error is raised
        * Duplicate files (duplicated file name): file is added to the audit table, DuplicateFileError is raised
        * Overwrites (duplicated message_id): file is not added to the audit table, UnhandledAuditTableError is raised
        """
        # Populate the table with some entries which are not in the same queue
        self.add_entry_to_table(MockAuditTableEntry.emis_flu_1_queued)  # different queue
        self.add_entry_to_table(MockAuditTableEntry.emis_rsv_1_queued)  # different queue
        self.add_entry_to_table(MockAuditTableEntry.ravs_flu_1_queued)  # different queue

        # Test case 1: new file with status of 'Processed'.
        # File should be added to the audit table, with status 'Processed'. Return value should be False.
        test_file_1 = AuditTableEntry("RAVS", "RSV", "YGM41", FileStatus.PROCESSED, file_number=1)

        result = upsert_audit_table(
            message_id=test_file_1.message_id,
            file_key=test_file_1.filename,
            created_at_formatted_str=test_file_1.created_at_formatted_string,
            queue_name=test_file_1.queue_name,
            file_status=FileStatus.PROCESSED,
            is_existing_file=False,
        )

        self.assertFalse(result)
        self.assert_table_entry(test_file_1, FileStatus.PROCESSED)

        # Test case 2: Duplicate file with status of 'Duplicate'.
        # Audit table status should be updated to 'Duplicate'. Return value should be False.
        test_file_2 = AuditTableEntry("RAVS", "RSV", "YGM41", FileStatus.DUPLICATE, file_number=2)
        test_file_2.filename = test_file_1.filename
        test_file_2.audit_table_entry[AuditTableKeys.FILENAME] = test_file_2.filename

        result = upsert_audit_table(
            message_id=test_file_2.message_id,
            file_key=test_file_2.filename,
            created_at_formatted_str=test_file_2.created_at_formatted_string,
            queue_name=test_file_2.queue_name,
            file_status=FileStatus.DUPLICATE,
            is_existing_file=False,
        )

        self.assertFalse(result)
        self.assert_table_entry(test_file_2, FileStatus.DUPLICATE)

        # Test case 3: new file with status of 'Processing', and no files ahead in the queue.
        # Audit table status should be updated to 'Processing'. Return value should be False.
        test_file_3 = AuditTableEntry("RAVS", "RSV", "YGM41", FileStatus.PROCESSING, file_number=3)

        result = upsert_audit_table(
            message_id=test_file_3.message_id,
            file_key=test_file_3.filename,
            created_at_formatted_str=test_file_3.created_at_formatted_string,
            queue_name=test_file_3.queue_name,
            file_status=FileStatus.PROCESSING,
            is_existing_file=False,
        )

        self.assertFalse(result)
        self.assert_table_entry(test_file_3, FileStatus.PROCESSING)

        # Test case 4: new file with status of 'Processing', and files ahead in the queue.
        # File should be added to the audit table, with status 'Queued'. Return value should be True.
        test_file_4 = AuditTableEntry("RAVS", "RSV", "YGM41", FileStatus.PROCESSING, file_number=4)

        result = upsert_audit_table(
            message_id=test_file_4.message_id,
            file_key=test_file_4.filename,
            created_at_formatted_str=test_file_4.created_at_formatted_string,
            queue_name=test_file_4.queue_name,
            file_status=FileStatus.PROCESSING,
            is_existing_file=False,
        )

        self.assertTrue(result)
        self.assert_table_entry(test_file_4, FileStatus.QUEUED)

        # Test case 5: existing file with status of 'Processing'.
        # Audit table status should be updated to 'Processing'. Return value should be False.
        result = upsert_audit_table(
            message_id=test_file_4.message_id,
            file_key=test_file_4.filename,
            created_at_formatted_str=test_file_4.created_at_formatted_string,
            queue_name=test_file_4.queue_name,
            file_status=FileStatus.PROCESSING,
            is_existing_file=True,
        )

        self.assertFalse(result)
        self.assert_table_entry(test_file_4, FileStatus.PROCESSING)

        # Test case 6: existing file with status of 'Processed'.
        # Audit table status should be updated to 'Processed'. Return value should be False.
        result = upsert_audit_table(
            message_id=test_file_4.message_id,
            file_key=test_file_4.filename,
            created_at_formatted_str=test_file_4.created_at_formatted_string,
            queue_name=test_file_4.queue_name,
            file_status=FileStatus.PROCESSED,
            is_existing_file=True,
        )

        self.assertFalse(result)
        self.assert_table_entry(test_file_4, FileStatus.PROCESSING)  # TODO: ?Should be processed

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
            "message_id": {"S": message_id_1},
            "filename": {"S": file_key_1},
            "queue_name": {"S": "test_queue"},
            "status": {"S": "Processing"},
            "timestamp": {"S": created_at_formatted_string_1},
        }

        # Test case 2: file_key_2 should be added to the audit table with status set to "Queued"
        expected_table_item_2 = {
            "message_id": {"S": message_id_2},
            "filename": {"S": file_key_2},
            "queue_name": {"S": "test_queue"},
            "status": {"S": "Queued"},
            "timestamp": {"S": created_at_formatted_string_2},
        }

        # Test case 3: file_key_1 should be added to the audit table again,
        # with status set to "Not processed - duplicate"
        expected_table_item_3 = {
            "message_id": {"S": message_id_3},
            "filename": {"S": file_key_1},
            "queue_name": {"S": "test_queue"},
            "status": {"S": "Not processed - duplicate"},
            "timestamp": {"S": created_at_formatted_string_3},
        }

        # Test case 4: file_key_4 should not be added to the audit table because the message_id is a duplicate.
        # Note that this scenario should never occur as a new unique message_id is generated for each file upload,
        # even if the file name is a duplicate, but this test is included for safety because default behaviour of
        # dynamodb is to overwrite the existing item if the message_id is the same.
        expected_table_item_4 = {
            "message_id": {"S": message_id_3},
            "filename": {"S": file_key_4},
            "queue_name": {"S": "test_queue"},
            "status": {"S": "Processed"},
            "timestamp": {"S": created_at_formatted_string_4},
        }

        # Add a file to the audit table
        self.assertFalse(
            upsert_audit_table(
                message_id_1,
                file_key_1,
                created_at_formatted_string_1,
                queue_name="test_queue",
                file_status="Processing",
                is_existing_file=False,
            )
        )
        table_items = self.get_table_items()
        assert len(table_items) == 1
        assert expected_table_item_1 in table_items

        # Add another file to the audit table
        self.assertTrue(
            upsert_audit_table(
                message_id_2,
                file_key_2,
                created_at_formatted_string_2,
                queue_name="test_queue",
                file_status="Processing",
                is_existing_file=False,
            )
        )
        table_items = self.get_table_items()
        assert len(table_items) == 2
        assert expected_table_item_1 in table_items
        assert expected_table_item_2 in table_items

        # Attempt to add the file 1 again
        self.assertFalse(
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
        table_items = self.get_table_items()
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
        table_items = self.get_table_items()
        assert len(table_items) == 3
        assert expected_table_item_1 in table_items
        assert expected_table_item_2 in table_items
        assert expected_table_item_3 in table_items
        assert expected_table_item_4 not in table_items
