import uuid
from pds import PdsService
from fhir_controller import FhirController, make_controller
from models.errors import Severity, Code, create_operation_outcome


def create_imms_handler(event, context):
    return create_immunization(event, make_controller())


def create_immunization(event, controller: FhirController):
    try:
        return controller.create_immunization(event)
    except Exception as e:
        exp_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                             code=Code.server_error,
                                             diagnostics=str(e))
        return FhirController.create_response(500, exp_error.json())

# event_body = event["body"]
#     nhs_number = event_body["nhs_number"]
#     pds_service = PdsService()
#     patient_response = pds_service.get_patient_details(nhs_number)