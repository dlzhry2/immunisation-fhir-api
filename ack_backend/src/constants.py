"""Constants for ack lambda"""

import os
from utils_for_ack_lambda import get_environment

ENVIRONMENT = get_environment()
SOURCE_BUCKET_NAME = f"immunisation-batch-{ENVIRONMENT}-data-sources"
ACK_BUCKET_NAME = os.getenv("ACK_BUCKET_NAME")
AUDIT_TABLE_NAME = os.environ["AUDIT_TABLE_NAME"]
AUDIT_TABLE_FILENAME_GSI = "filename_index"
AUDIT_TABLE_QUEUE_NAME_GSI = "queue_name_index"


class Constants:
    """Constants for ack lambda"""

    ack_headers = [
        "MESSAGE_HEADER_ID",
        "HEADER_RESPONSE_CODE",
        "ISSUE_SEVERITY",
        "ISSUE_CODE",
        "ISSUE_DETAILS_CODE",
        "RESPONSE_TYPE",
        "RESPONSE_CODE",
        "RESPONSE_DISPLAY",
        "RECEIVED_TIME",
        "MAILBOX_FROM",
        "LOCAL_ID",
        "IMMS_ID",
        "OPERATION_OUTCOME",
        "MESSAGE_DELIVERY",
    ]
