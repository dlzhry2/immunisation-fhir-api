import argparse
import logging
import pprint
import uuid


from fhir_controller import FhirController, make_controller
from local_lambda import load_string
from models.errors import Severity, Code, create_operation_outcome
from log_structure import function_info
from constants import GENERIC_SERVER_ERROR_DIAGNOSTICS_MESSAGE

logging.basicConfig(level="INFO")
logger = logging.getLogger()

controller: FhirController = make_controller()

@function_info
def create_imms_handler(event, _context):
    return create_immunization(event)


def create_immunization(event):
    try:
        return controller.create_immunization(event)
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
    parser = argparse.ArgumentParser("create_imms_handler")
    parser.add_argument("path", help="Path to Immunization JSON file.", type=str)
    args = parser.parse_args()

    event = {
        "body": load_string(args.path),
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "AuthenticationType": "ApplicationRestricted",
        },
    }

    pprint.pprint(event)
    pprint.pprint(create_imms_handler(event, {}))
