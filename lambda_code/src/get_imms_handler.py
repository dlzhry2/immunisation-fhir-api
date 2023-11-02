import uuid

from dynamodb import EventTable
import json
import re


def create_response(event_id, message, code):
    return {
        "resourceType": "OperationOutcome",
        "id": event_id,
        "meta": {
            "profile": [
                "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
            ]
        },
        "issue": [
            {
                "severity": "error",
                "code": code,
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                            "code": code.upper()
                        }
                    ]
                },
                "diagnostics": message
            }
        ]
    }


def get_imms_handler(event, context):
    dynamo_service = EventTable()
    return get_imms(event, dynamo_service)


# create function which receives event and instance of dynamodb
def get_imms(event, dynamo_service):
    event_id = event["pathParameters"]["id"]

    def is_valid_id(_event_id):
        pattern = r'^[A-Za-z0-9\-.]{1,64}$'
        return re.match(pattern, _event_id) is not None

    if not is_valid_id(event_id) or not event_id:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": json.dumps(
                create_response(str(uuid.uuid4()),
                                "he provided event ID is either missing or not in the expected format.",
                                "invalid"))
        }

    message = dynamo_service.get_event_by_id(event_id)
    if message is None:

        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/fhir+json",
            },
            "body": json.dumps(create_response(str(uuid.uuid4()), "The requested resource was not found.", "not-found"))
        }

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/fhir+json",
        },
        'body': json.dumps(message)
    }
