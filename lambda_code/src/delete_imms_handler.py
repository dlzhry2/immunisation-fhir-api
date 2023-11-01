import json
from dynamodb import EventTable
import re


def delete_imms_handler(event, context):
    event_id = event["pathParameters"]["id"]
    dynamo_service = EventTable()
    
    def is_valid_id(event_id):
        pattern = r'^[A-Za-z0-9\-.]{1,64}$'
        return re.match(pattern, event_id) is not None
    
    if not is_valid_id(event_id) or not event_id:
        return {
        "statusCode": 400,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "resourceType": "OperationOutcome",
            "id": "a5abca2a-4eda-41da-b2cc-95d48c6b791d",
            "meta": {
                "profile": [
                    "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
                ]
            },
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                                "code": "INVALID"
                            }
                        ]
                    },
                    "diagnostics": "The provided event ID is either missing or not in the expected format."
                }
            ]
        })
    }
    
    message = dynamo_service.delete_event(event_id)
    response = {
            "statusCode": 200,  # HTTP status code
            "body": json.dumps({
                "message": message  
            })
        }
    return response
