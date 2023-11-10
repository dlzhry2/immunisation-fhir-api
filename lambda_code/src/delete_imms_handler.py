import json
import re

from fhir_controller import FhirController, make_controller


def delete_imms_handler(event, context):
    return delete_immunization(event, make_controller())


def delete_immunization(event, controller: FhirController):
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
            "body": json.dumps(
                create_response("The provided event ID is either missing or not in the expected format.", "invalid"))}

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
