from typing import Optional

from fhir.resources.immunization import Immunization

from fhir_repository import ImmunisationRepository


class FhirService:

    def __init__(self, imms_repo: ImmunisationRepository):
        self.immunisation_repo = imms_repo

    def get_immunisation_by_id(self, imms_id: str) -> Optional[Immunization]:
        imms = self.immunisation_repo.get_immunisation_by_id(imms_id)
        return Immunization.parse_obj(imms)
