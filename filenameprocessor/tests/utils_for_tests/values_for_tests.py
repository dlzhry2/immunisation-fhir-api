"""File of values which can be used for testing"""

# Mock_created_at_formatted string is used throughout the test suite, so that the ack file name
# (which includes the created_at_formatted_string) can be predicted.
MOCK_CREATED_AT_FORMATTED_STRING = "20211120T12000000"


class BucketNames:
    """Class to hold bucket names for use in tests"""

    CONFIG = "immunisation-batch-internal-dev-data-configs"
    SOURCE = "immunisation-batch-internal-dev-data-sources"
    DESTINATION = "immunisation-batch-internal-dev-data-destinations"


class Firehose:
    """Class containing Firehose values for use in tests"""

    STREAM_NAME = "immunisation-fhir-api-internal-dev-splunk-firehose"


class Sqs:
    """Class to hold SQS values for use in tests"""

    ATTRIBUTES = {"FifoQueue": "true", "ContentBasedDeduplication": "true"}
    QUEUE_NAME = "imms-batch-internal-dev-metadata-queue.fifo"


# Dictionary for mocking the os.environ dict
# NOTE: FILE_NAME_GSI and CONFIG_BUCKET_NAME environment variables are set in the terraform,
# but not used in the src code and so are not set here.
MOCK_ENVIRONMENT_DICT = {
    "SOURCE_BUCKET_NAME": BucketNames.SOURCE,
    "ACK_BUCKET_NAME": BucketNames.DESTINATION,
    "QUEUE_URL": "https://sqs.eu-west-2.amazonaws.com/123456789012/imms-batch-internal-dev-metadata-queue.fifo",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "SPLUNK_FIREHOSE_NAME": Firehose.STREAM_NAME,
    "AUDIT_TABLE_NAME": "immunisation-batch-internal-dev-audit-table",
    "FILE_NAME_PROC_LAMBDA_NAME": "imms-batch-internal-dev-filenameproc_lambda",
}


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
