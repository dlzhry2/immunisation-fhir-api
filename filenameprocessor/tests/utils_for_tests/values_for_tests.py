"""File of values which can be used for testing"""

from unittest.mock import patch
from datetime import datetime

from tests.utils_for_tests.mock_environment_variables import MOCK_ENVIRONMENT_DICT

with patch.dict("os.environ", MOCK_ENVIRONMENT_DICT):
    from constants import FileStatus, AuditTableKeys


fixed_datetime = datetime(2024, 10, 29, 12, 0, 0)

# Mock_created_at_formatted string is used throughout the test suite, so that the ack file name
# (which includes the created_at_formatted_string) can be predicted.
MOCK_CREATED_AT_FORMATTED_STRING = "20211120T12000000"


class FileDetails:
    """
    Class to create and hold values for a mock file, based on the vaccine type, supplier and ods code.
    NOTE: Supplier and ODS code are hardcoded rather than mapped, for testing purposes.
    NOTE: The permissions_list and permissions_config are examples of full permissions for the suppler for the
    vaccine type.
    """

    def __init__(self, vaccine_type: str, supplier: str, ods_code: str):
        self.name = f"{vaccine_type.upper()}/ {supplier.upper()} file"
        self.created_at_formatted_string = MOCK_CREATED_AT_FORMATTED_STRING
        self.file_key = f"{vaccine_type}_Vaccinations_v5_{ods_code}_20240708T12130100.csv"
        self.ack_file_key = (
            f"ack/{vaccine_type}_Vaccinations_v5_{ods_code}_20240708T12130100"
            + f"_InfAck_{MOCK_CREATED_AT_FORMATTED_STRING}.csv"
        )
        self.vaccine_type = vaccine_type
        self.ods_code = ods_code
        self.supplier = supplier
        self.message_id = f"{vaccine_type.lower()}_{supplier.lower()}_test_id"
        self.queue_name = f"{supplier}_{vaccine_type}"
        self.permissions_list = [f"{vaccine_type}_FULL"]
        self.permissions_config = {self.supplier: self.permissions_list}
        # DO NOT CHANGE THE SQS MESSAGE BODY UNLESS THE IMPLEMENTATION OF THE MESSAGE BODY IS CHANGED - IT IS USED
        # FOR TEST ASSERTIONS TO ENSURE TEH SQS MESSAGE BODY IS AS EXPECTED
        self.sqs_message_body = {
            "message_id": self.message_id,
            "vaccine_type": self.vaccine_type,
            "supplier": self.supplier,
            "filename": self.file_key,
            "permission": self.permissions_list,
            "created_at_formatted_string": self.created_at_formatted_string,
        }


class MockFileDetails:
    """Class containing mock file details for use in tests"""

    rsv_ravs = FileDetails("RSV", "RAVS", "X26")
    flu_emis = FileDetails("FLU", "EMIS", "YGM41")


class AuditTableEntry:
    """
    Class to create and hold values for a mock file, based on the vaccine type, supplier and ods code.
    NOTE: Supplier and ODS code are hardcoded rather than mapped, for testing purposes.
    NOTE: The permissions_list and permissions_config are examples of full permissions for the suppler for the
    vaccine type.
    """

    def __init__(
        self, supplier: str, vaccine_type: str, ods_code: str, status: str = FileStatus.QUEUED, file_number: str = 1
    ):
        file_date_and_time_string = f"20000101T0000000{file_number}"
        self.message_id = f"{supplier.lower()}_{vaccine_type.lower()}_test_id_{file_number}"
        self.filename = f"{vaccine_type}_Vaccinations_v5_{ods_code}_{file_date_and_time_string}.csv"
        self.queue_name = f"{supplier}_{vaccine_type}"
        self.created_at_formatted_string = f"200{file_number}0101T00000000"
        self.status = status
        
        self.audit_table_entry = {
            AuditTableKeys.MESSAGE_ID: self.message_id,
            AuditTableKeys.FILENAME: self.filename,
            AuditTableKeys.QUEUE_NAME: self.queue_name,
            AuditTableKeys.STATUS: self.status,
            AuditTableKeys.TIMESTAMP: self.created_at_formatted_string,
        }


class MockAuditTableEntry:
    """Class containing mock file details for use in tests"""

    ravs_rsv_1_processed = AuditTableEntry("RAVS", "RSV", "X26", FileStatus.PROCESSED, file_number=1)
    ravs_rsv_2_queued = AuditTableEntry("RAVS", "RSV", "X26", FileStatus.QUEUED, file_number=2)
    ravs_rsv_3_queued = AuditTableEntry("RAVS", "RSV", "X26", FileStatus.QUEUED, file_number=3)
    ravs_rsv_4_queued = AuditTableEntry("RAVS", "RSV", "X26", FileStatus.QUEUED, file_number=4)
    emis_flu_1_queued = AuditTableEntry("EMIS", "FLU", "YGM41")
    emis_rsv_1_queued = AuditTableEntry("EMIS", "RSV", "YGM41")
    ravs_flu_1_queued = AuditTableEntry("RAVS", "FLU", "X26")
