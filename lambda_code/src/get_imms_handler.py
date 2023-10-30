from dynamodb import EventTable
import json
import re

def get_imms_handler(event, context):
    dynamo_service = EventTable()
    return get_imms(event, dynamo_service)
    # run get request to API_gateway to see what event object looks like when it comes through
    # Check what the return value of message is when event is not found
    
    
# create function which recieves event and instance of dynamodb
def get_imms(event, dynamo_service):
    event_id = event.get("id")
    
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
