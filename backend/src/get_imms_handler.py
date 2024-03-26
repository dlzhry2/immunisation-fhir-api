import argparse
import pprint
import uuid

from fhir_controller import FhirController, make_controller
from models.errors import Severity, Code, create_operation_outcome
from timer import timed


@timed
def get_imms_handler(event, context):
    headers = event.get('headers', {})
    print("event:", event)
    correlation_id = headers.get('X-Correlation-ID', 'X-Correlation-ID not passed')
    request_id = headers.get('X-Request-ID', 'X-Request-ID not passed')
    path = event.get('path', 'Unknown')
    resource_path = event['requestContext']['resourcePath']
    print({
        "correlation_id": correlation_id,
        "request_id": request_id,
        "resource_path": resource_path,
        "actual_path": path
    })
    print(f"Request ID: {request_id}, Correlation ID: {correlation_id}, Path: {path}")
    return get_immunization_by_id(event, make_controller())


def get_immunization_by_id(event, controller: FhirController):
    try:
        return controller.get_immunization_by_id(event)
    except Exception as e:
        exp_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                             code=Code.server_error,
                                             diagnostics=str(e))
        return FhirController.create_response(500, exp_error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("get_imms_handler")
    parser.add_argument("id", help="Id of Immunization.", type=str)
    args = parser.parse_args()

    event = {
        "pathParameters": {
            "id": args.id
        }
    }
    pprint.pprint(get_imms_handler(event, {}))
