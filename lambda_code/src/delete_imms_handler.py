import json
from dynamodb import EventTable
import re
from utilities.create_operation_outcome import create_response

def delete_imms_handler(event, context):
    dynamo_service = EventTable()
    return delete_imms(event, dynamo_service)

def delete_imms(event, dynamo_service):
    event_id = event["pathParameters"]["id"]
    
    def is_valid_id(event_id):
        pattern = r'^[A-Za-z0-9\-.]{1,64}$'
        return re.match(pattern, event_id) is not None
    
    if not is_valid_id(event_id) or not event_id:
        return {
        "statusCode": 400,
        "headers": {
            "Content-Type": "application/fhir+json",
        },
        "body": json.dumps(create_response("The provided event ID is either missing or not in the expected format.", "invalid"))}
    
    message = dynamo_service.delete_event(event_id)
    
    if message is None:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": json.dumps(create_response("The requested resource was not found.", "not-found"))
        }
        
    response = {
            "statusCode": 200,
            "body": message  
        }
    return response
