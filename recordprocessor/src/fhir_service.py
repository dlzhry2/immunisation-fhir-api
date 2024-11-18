from pydantic import ValidationError
from fhir_repository import ImmunizationRepository
from fhir.resources.R4B.immunization import Immunization


class FhirService:
    def __init__(self, imms_repo: ImmunizationRepository):
        self.immunization_repo = imms_repo

    def create_immunization(
        self, immunization: any, supplier_system: str, vax_type: str
    ) -> Immunization:

        imms = self.immunization_repo.create_immunization(
            immunization,
            supplier_system,
            vax_type
        )

        return Immunization.parse_obj(imms)
