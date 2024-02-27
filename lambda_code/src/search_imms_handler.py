import base64

import argparse
import pprint
import uuid

from aws_lambda_typing import context as context_, events

from fhir_controller import FhirController, make_controller
from models.errors import Severity, Code, create_operation_outcome


def search_imms_handler(event: events.APIGatewayProxyEventV1, context: context_):
    return search_imms(event, make_controller())


def search_imms(event: events.APIGatewayProxyEventV1, controller: FhirController):
    try:
        return controller.search_immunizations(event)
    except Exception as e:
        exp_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                             code=Code.server_error,
                                             diagnostics=str(e))
        return FhirController.create_response(500, exp_error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("search_imms_handler")
    parser.add_argument("--nhsNumber", help="Identifier of Patient", type=str, required=True)
    parser.add_argument(
        "--diseaseType",
        help="http://hl7.org/fhir/ValueSet/immunization-target-disease",
        type=str,
        required=True,
        nargs="+")
    args = parser.parse_args()

    event: events.APIGatewayProxyEventV1 = {
        "multiValueQueryStringParameters": {
            "-nhsNumber": [args.nhsNumber],
            "-diseaseType": [",".join(args.diseaseType)]
        },
        "httpMethod": "POST",
        "headers": {'Content-Type': 'application/x-www-form-urlencoded'},
        "body": base64.b64encode("-diseaseType=1234".encode("utf-8")),
        "resource": None,
        "isBase64Encoded": None,
        "multiValueHeaders": None,
        "path": None,
        "pathParameters": None,
        "queryStringParameters": None,
        "requestContext": None,
    }
    pprint.pprint(search_imms_handler(event, {}))
