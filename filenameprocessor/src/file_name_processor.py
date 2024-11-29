"""
Lambda function for the filenameprocessor lambda. Files received may be from the data sources bucket (for row-by-row
processing) or the config bucket (for uploading to cache).
NOTE: The expected file format for incoming files from the data sources bucket is 
'VACCINETYPE_Vaccinations_version_ODSCODE_DATETIME.csv'. e.g. 'Flu_Vaccinations_v5_YYY78_20240708T12130100.csv'
(ODS code has multiple lengths)
"""

import logging
from uuid import uuid4
from initial_file_validation import initial_file_validation, get_supplier_permissions
from send_sqs_message import make_and_send_sqs_message
from make_and_upload_ack_file import make_and_upload_the_ack_file
from audit_table import add_to_audit_table
from clients import s3_client
from elasticcache import upload_to_elasticache
from log_structure import logging_decorator
from utils_for_filenameprocessor import extract_file_key_elements

logging.basicConfig(level="INFO")
logger = logging.getLogger()
logger.setLevel("INFO")


# NOTE: logging_decorator is applied to handle_record function, rather than lambda_handler, because
# the logging_decorator is for an individual record, whereas the lambda_handle could potentially be handling
# multiple records.
@logging_decorator
def handle_record(record) -> dict:
    """Processes a single record based on whether it came from the 'data-sources' or 'config' bucket.
    Returns a dictionary containing information to be included in the logs."""
    try:
        bucket_name = record["s3"]["bucket"]["name"]
        file_key = record["s3"]["object"]["key"]
    except Exception as error:  # pylint: disable=broad-except
        logger.error("Error obtaining file_key: %s", error)
        return {"statusCode": 500, "message": "Failed to download file key", "error": str(error)}

    if "data-sources" in bucket_name:
        try:
            message_id = str(uuid4())  # Assign a unique message_id for the file

            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            created_at_formatted_string = response["LastModified"].strftime("%Y%m%dT%H%M%S00")

            added_to_audit_table = add_to_audit_table(message_id, file_key, created_at_formatted_string)

            validation_passed = initial_file_validation(file_key) if added_to_audit_table else False
            message_delivered = False
            if validation_passed:
                # Try to send to sqs
                file_key_elements = extract_file_key_elements(file_key)
                vaccine_type = file_key_elements["vaccine_type"]
                supplier = file_key_elements["supplier"]
                permission = get_supplier_permissions(supplier=supplier)
                message_delivered = make_and_send_sqs_message(
                    file_key, message_id, permission, created_at_formatted_string
                )

            if message_delivered:
                return {
                    "statusCode": 200,
                    "message": "Successfully sent to SQS queue",
                    "file_key": file_key,
                    "message_id": message_id,
                    "supplier": supplier,
                    "vaccine_type": vaccine_type,  # pylint: disable = possibly-used-before-assignment
                }
            else:
                make_and_upload_the_ack_file(message_id, file_key, message_delivered, created_at_formatted_string)
                return {
                    "statusCode": 400,
                    "message": "Infrastructure Level Response Value - Processing Error",
                    "file_key": file_key,
                    "message_id": message_id,
                }

        except Exception as error:  # pylint: disable=broad-except
            # If an unexpected error occured, upload an ack file
            logging.error("Error processing file'%s': %s", file_key, str(error))
            if "message_id" not in locals():
                message_id = "Message id was not created"
            message_delivered = False
            if "created_at_formatted_string" not in locals():
                created_at_formatted_string = "created_at_time_not_identified"
            make_and_upload_the_ack_file(message_id, file_key, message_delivered, created_at_formatted_string)
            return {
                "statusCode": 500,
                "message": "Infrastructure Level Response Value - Processing Error",
                "file_key": file_key,
                "message_id": message_id,
                "error": str(error),
            }

    elif "config" in bucket_name:
        try:
            upload_to_elasticache(file_key, bucket_name)
            logger.info("%s content successfully uploaded to cache", file_key)
            return {"statusCode": 200, "message": "File content successfully uploaded to cache", "file_key": file_key}
        except Exception as error:  # pylint: disable=broad-except
            logger.error("Error uploading to cache for file '%s': %s", file_key, error)
            return {
                "statusCode": 500,
                "message": "Failed to upload file content to cache",
                "file_key": file_key,
                "error": str(error),
            }

    else:
        logger.error("Unable to proecess file %s due to unexpected bucket name %s", file_key, bucket_name)
        return {
            "statusCode": 500,
            "message": f"Failed to process file due to unexpected bucket name {bucket_name}",
            "file_key": file_key,
        }


def lambda_handler(event: dict, context) -> None:  # pylint: disable=unused-argument
    """Lambda handler for filenameprocessor lambda. Processes each record in event records."""

    for record in event["Records"]:
        handle_record(record)
