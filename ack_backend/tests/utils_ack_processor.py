"""Values for use in ack_processor tests"""

from datetime import datetime

SOURCE_BUCKET_NAME = "immunisation-batch-internal-dev-data-sources"
DESTINATION_BUCKET_NAME = "immunisation-batch-internal-dev-data-destinations"
CONFIG_BUCKET_NAME = "immunisation-batch-internal-dev-configs"
STREAM_NAME = "imms-batch-internal-dev-processingdata-stream"

AWS_REGION = "eu-west-2"
STATIC_DATETIME = datetime(2021, 11, 20, 12, 0, 0)
# For test purposes static time with no seconds
STATIC_ISO_DATETIME = STATIC_DATETIME.replace(second=0, microsecond=0).isoformat(timespec="milliseconds")
