import uuid

from fhir_controller import FhirController
from fhir_repository import ImmunisationRepository
from fhir_service import FhirService
from models.errors import Severity, Code, create_operation_outcome


def get_imms_handler(event, context):
    imms_repo = ImmunisationRepository()
    service = FhirService(imms_repo=imms_repo)
    controller = FhirController(fhir_service=service)

    return get_immunisation_by_id(event, controller)


def get_immunisation_by_id(event, controller: FhirController):
    try:
        return controller.get_immunisation_by_id(event)
    except Exception as e:
        exp_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                             code=Code.not_found,
                                             diagnostics=str(e))
        return FhirController.create_response(500, exp_error.json())
