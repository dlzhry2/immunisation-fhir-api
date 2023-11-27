from typing import Optional
from fhir.resources.immunization import Immunization
from fhir_repository import ImmunisationRepository


class FhirService:
    def __init__(self, imms_repo: ImmunisationRepository):
        self.immunisation_repo = imms_repo
        

    def get_immunization_by_id(self, imms_id: str) -> Optional[Immunization]:
        imms = self.immunisation_repo.get_immunization_by_id(imms_id)
        if imms:
            # TODO: This shouldn't raise an exception since, we validate the message before storing it,
            #  but what if the stored message is different from the requested FHIR version?
            return Immunization.parse_obj(imms)
        else:
            return None

    def delete_immunization(self, imms_id) -> Optional[Immunization]:
        """Delete an Immunization if it exits and return the ID back if successful.
        Exception will be raised if resource didn't exit. Multiple calls to this method won't change the
        record in the database.
        """
        imms = self.immunisation_repo.delete_immunization(imms_id)
        return Immunization.parse_obj(imms)
