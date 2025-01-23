"""Add the filename to the audit table and check for duplicates."""

from typing import Union
from boto3.dynamodb.conditions import Key
from clients import dynamodb_client, dynamodb_resource, logger
from errors import UnhandledAuditTableError
from constants import AUDIT_TABLE_NAME, AUDIT_TABLE_FILENAME_GSI, AUDIT_TABLE_QUEUE_NAME_GSI


def update_audit_table_status(file_key: str) -> str:
    """Updates the status in the audit table to 'Processed' and returns the queue name."""
    try:
        file_details_in_audit_table = (
            dynamodb_resource.Table(AUDIT_TABLE_NAME)
            .query(IndexName=AUDIT_TABLE_FILENAME_GSI, KeyConditionExpression=Key("filename").eq(file_key))
            .get("Items", [])[0]
        )
        message_id = file_details_in_audit_table.get("message_id")

        # Update the status in the audit table to "Processed"
        dynamodb_client.update_item(
            TableName=AUDIT_TABLE_NAME,
            Key={"message_id": {"S": message_id}},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": {"S": "Processed"}},
            ConditionExpression="attribute_exists(message_id)",
        )

        logger.info(
            "%s file, with message id %s, and the status successfully updated to audit table", file_key, message_id
        )

        return file_details_in_audit_table.get("queue_name")

    except Exception as error:  # pylint: disable = broad-exception-caught
        logger.error(error)
        raise UnhandledAuditTableError(error) from error


def get_queued_file_details(queue_name: str) -> Union[dict, None]:
    """
    Checks for queued files.
    Returns a dictionary containing the details of the oldest queued file, or returns None if no queued files are found.
    """
    queued_files_found_in_audit_table = dynamodb_resource.Table(AUDIT_TABLE_NAME).query(
        IndexName=AUDIT_TABLE_QUEUE_NAME_GSI,
        KeyConditionExpression=Key("queue_name").eq(queue_name) & Key("status").eq("Queued"),
    )

    if not queued_files_found_in_audit_table["Items"]:
        return None

    queued_files_sorted_by_timestamp = sorted(queued_files_found_in_audit_table["Items"], key=lambda x: x["timestamp"])
    return queued_files_sorted_by_timestamp[0]
