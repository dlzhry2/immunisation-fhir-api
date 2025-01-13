"""Add the filename to the audit table and check for duplicates."""

import os
from boto3.dynamodb.conditions import Key
from clients import dynamodb_client, dynamodb_resource, logger
from errors import DuplicateFileError, UnhandledAuditTableError, ProcessingError


def add_to_audit_table(
    message_id: str,
    file_key: str,
    created_at_formatted_str: str,
    queue_name: str,
    process_status: str,
    query_type: str
) -> None:
    """
    Adds the filename to the audit table.
    Raises an error if the file is a duplicate (after adding it to the audit table).
    """
    try:
        table_name = os.environ["AUDIT_TABLE_NAME"]
        file_name_gsi = "filename_index"
        queue_name_gsi = "queue_name_index"
        processing_exists = False
        if query_type == "update":
            dynamodb_client.update_item(
                TableName=table_name,
                Key={"filename": {"S": file_key}},
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": {"S": "Processing"}},
                ConditionExpression="attribute_exists(file_key)",
            )
            logger.info("%s file set for processing, and the status successfully updated to audit table", file_key)
            return None
        # Check for duplicates before adding to the table (if the query returns any items, then the file is a duplicate)
        file_name_response = dynamodb_resource.Table(table_name).query(
            IndexName=file_name_gsi, KeyConditionExpression=Key("filename").eq(file_key)
        )
        duplicate_exists = bool(file_name_response.get("Items"))

        # Check for files un der processing for Supplier_Vaccine combination, if yes queue file for processing
        if not duplicate_exists:
            queue_response = dynamodb_resource.Table(table_name).query(
                IndexName=queue_name_gsi,
                KeyConditionExpression=Key("queue_name").eq(queue_name)
                & Key("status").eq(process_status),
            )
            if queue_response["Items"]:
                process_status = "Queued"
                processing_exists = True

        # Add to the audit table (regardless of whether it is a duplicate)
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                "message_id": {"S": message_id},
                "filename": {"S": file_key},
                "queue_name": {"S": queue_name},
                "status": {
                    "S": (
                        "Not processed - duplicate"
                        if duplicate_exists
                        else process_status
                    )
                },
                "timestamp": {"S": created_at_formatted_str},
            },
            ConditionExpression="attribute_not_exists(message_id)",  # Prevents accidental overwrites
        )
        logger.info(
            "%s file, with message id %s, successfully added to audit table",
            file_key,
            message_id,
        )

    except Exception as error:  # pylint: disable = broad-exception-caught
        error_message = f"Error adding {file_key} to the audit table"
        logger.error(error_message)
        raise UnhandledAuditTableError(error_message) from error

    # If a duplicte exists, raise an exception
    if duplicate_exists:
        logger.error(
            "%s file duplicate added to s3 at the following time: %s",
            file_key,
            created_at_formatted_str,
        )
        raise DuplicateFileError(f"Duplicate file: {file_key}")

    # If processing exists for supplier_vaccine, raise an exception
    if processing_exists:
        logger.error(
            "%s file queued for processing at time: %s",
            file_key,
            created_at_formatted_str,
        )
        raise ProcessingError(f"Queued File: {file_key}")


def check_queue(queue_name: str):

    table_name = os.environ["AUDIT_TABLE_NAME"]
    queue_name_gsi = "queue_name_index"

    queue_response = dynamodb_resource.Table(table_name).query(
            IndexName=queue_name_gsi,
            KeyConditionExpression=Key("queue_name").eq(queue_name)
            & Key("status").eq("Queued"),
        )
    if queue_response["Items"]:
        file_name, message_id = get_file_name(queue_response)
        return file_name, message_id
    else:
        return None


def get_file_name(queue_response: dict):
    sorted_item = sorted(queue_response["Items"], key=lambda x: x["timestamp"])
    first_record = sorted_item[0]
    file_name = first_record.get("filename")
    message_id = first_record.get("message_id")
    return file_name, message_id
