"""Add the filename to the audit table and check for duplicates."""
 
import os
from boto3.dynamodb.conditions import Key,Attr
from clients import dynamodb_client, dynamodb_resource, logger
from errors import UnhandledAuditTableError
 
 
def add_to_audit_table(file_key: str, created_at_formatted_str: str) -> None:
    """
    Adds the filename to the audit table.
    Raises an error if the file is a duplicate (after adding it to the audit table).
    """
    try:
        table_name = os.environ["AUDIT_TABLE_NAME"]
        file_name_gsi = "filename_index"
        print("process_started")
        # Check for duplicates before adding to the table (if the query returns any items, then the file is a duplicate)
        file_name_response = dynamodb_resource.Table(table_name).query(
            IndexName=file_name_gsi, KeyConditionExpression=Key("filename").eq(file_key)
        )
        print(f"file_name_response:{file_name_response}")
        items = file_name_response.get("Items", [])
        print(f"items:{items}")
        message_id = items[0].get("message_id")
        queue_name = items[0].get("queue_name")
        # Add to the audit table (regardless of whether it is a duplicate)
        dynamodb_client.update_item(
            TableName=table_name,
            Key={"message_id": {"S": message_id}},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": {"S": "Processed"}},
            ConditionExpression="attribute_exists(message_id)"
        )
        logger.info("%s file, with message id %s, and the status successfully updated to audit table", file_key, message_id)
        return queue_name
    except Exception as error:  # pylint: disable = broad-exception-caught
        error_message = error #f"Error adding {file_key} to the audit table"
        logger.error(error_message)
        raise UnhandledAuditTableError(error_message) from error