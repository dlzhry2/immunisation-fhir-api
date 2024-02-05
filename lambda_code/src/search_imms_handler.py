import uuid

from fhir_controller import FhirController, make_controller
from models.errors import Severity, Code, create_operation_outcome


def search_imms_handler(event, context):
    return search_imms(event, make_controller())


def search_imms(event, controller: FhirController):
    try:
        return controller.search_immunizations(event)
    except Exception as e:
        exp_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                             code=Code.server_error,
                                             diagnostics=str(e))
        return FhirController.create_response(500, exp_error)
