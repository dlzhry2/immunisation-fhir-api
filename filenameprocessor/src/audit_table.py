import os
import logging
from boto3.dynamodb.conditions import Key
from clients import dynamodb_client, dynamodb_resource


logger = logging.getLogger()


def add_to_audit_table(message_id: str, file_key: str, created_at_formatted_str: str) -> bool:
    """
    Add the filename to the audit table. Returns true if no duplicates exist and the file is successfully added to
    the audit table, else false.
    """
    try:
        table_name = os.environ["AUDIT_TABLE_NAME"]
        gsi_name = os.environ["FILE_NAME_GSI"]

        # Check for duplicates (if the query returns any items, then the file is a duplicate)
        file_name_response = dynamodb_resource.Table(table_name).query(
            IndexName=gsi_name, KeyConditionExpression=Key("filename").eq(file_key)
        )

        if duplicate_exists := bool(file_name_response.get("Items")):
            logger.error("%s file duplicate added to s3 at the following time: %s", file_key, created_at_formatted_str)

        # Add to the audit table (regardless of where it is a duplicate)
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                "message_id": {"S": message_id},
                "filename": {"S": file_key},
                "status": {"S": "Processed"},
                "timestamp": {"S": created_at_formatted_str},
            },
        )

        logger.info("%s file, with message id %s, successfully added to audit table", file_key, message_id)
        return not duplicate_exists
    except Exception:  # pylint: disable = broad-exception-caught
        return False
