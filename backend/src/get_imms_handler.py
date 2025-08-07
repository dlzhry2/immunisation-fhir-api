import argparse
import logging
import pprint
import uuid


from fhir_controller import FhirController, make_controller
from models.errors import Severity, Code, create_operation_outcome
from log_structure import function_info
from constants import GENERIC_SERVER_ERROR_DIAGNOSTICS_MESSAGE

logging.basicConfig(level="INFO")
logger = logging.getLogger()

controller: FhirController = make_controller()

@function_info
def get_imms_handler(event, _context):
    return get_immunization_by_id(event)


def get_immunization_by_id(event):
    try:
        return controller.get_immunization_by_id(event)
    except Exception:  # pylint: disable = broad-exception-caught
        logger.exception("Unhandled exception")
        exp_error = create_operation_outcome(
            resource_id=str(uuid.uuid4()),
            severity=Severity.error,
            code=Code.server_error,
            diagnostics=GENERIC_SERVER_ERROR_DIAGNOSTICS_MESSAGE,
        )
        return FhirController.create_response(500, exp_error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("get_imms_handler")
    parser.add_argument("id", help="Id of Immunization.", type=str)
    args = parser.parse_args()

    event = {
        "pathParameters": {"id": args.id},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "AuthenticationType": "ApplicationRestricted",
        },
    }
    pprint.pprint(get_imms_handler(event, {}))
