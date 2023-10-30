from .dynamodb import EventTable
import json
import re

def get_imms_handler(event, context):
    event_id = event.get("id")
    dynamo_service = EventTable()
    
    def is_valid_id(event_id):
        pattern = r'^[A-Za-z0-9\-.]{1,64}$'
        return re.match(pattern, event_id) is not None
    
    if not is_valid_id(event_id) or not event_id:
        return {
            'statusCode': 400,
            'body': 'ID is not formatted correctly or is missing'
        }
    
    message = dynamo_service.get_event_by_id(event_id)
    
    if message is None:
        return {
            'statusCode': 404,
            'body': 'Event not found'
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': message})
    }
