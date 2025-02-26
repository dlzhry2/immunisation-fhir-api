import boto3
import os

# Get the DynamoDB table name from environment variables
table_name = "imms-internal-dev-imms-events"

if not table_name:
    raise ValueError("DYNAMODB_TABLE_NAME environment variable is not set")

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)

def clear_dynamodb():
    print(f"Clearing DynamoDB table: {table_name}")
    
    scan = table.scan()
    items = scan.get("Items", [])
    
    for item in items:
        table.delete_item(Key={"primary_key": item["primary_key"]})  # Change "primary_key" to your table's primary key attribute
    
    print(f"Deleted {len(items)} items from DynamoDB")

if __name__ == "__main__":
    clear_dynamodb()
