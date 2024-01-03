from typing import Optional
from fhir.resources.immunization import Immunization
from fhir.resources.list import List as FhirList
from fhir_repository import ImmunisationRepository
from models.errors import InvalidPatientId
from pds_service import PdsService
from s_flag_handler import remove_personal_info


class FhirService:
    def __init__(self, imms_repo: ImmunisationRepository, pds_service: PdsService):
        self.immunisation_repo = imms_repo
        self.pds_service = pds_service

    def get_immunization_by_id(self, imms_id: str) -> Optional[Immunization]:
      imms = self.immunisation_repo.get_immunization_by_id(imms_id)
      bundle = imms['resourceType'] == "Bundle"

      nhs_number = imms['patient']['identifier']['value'] if imms['resourceType'] == "Immunization" else imms["entry"][0]['patient']['identifier']['value']
      patient = self.pds_service.get_patient_details(nhs_number)
      patient_is_restricted = patient['meta']['security'][0]['display']

      if patient_is_restricted == "restricted":
          filtered_immunization = remove_personal_info(imms['entry'][0]) if bundle else remove_personal_info(imms)
          print(filtered_immunization, "<<<<<<<<<< FILTERED IMMUNZATION")
          print(Immunization.parse_obj(filtered_immunization), "<<<<<<<<< RESTRICTED PARSED AND FILTERED IMMS")
          return Immunization.parse_obj(filtered_immunization)
      else:
          print(Immunization.parse_obj(imms), "<<<<<<<<< PARSED IMMS")
          return Immunization.parse_obj(imms)

    def create_immunization(self, immunization: dict) -> Immunization:
        nhs_number = immunization['patient']['identifier']['value']
        patient = self.pds_service.get_patient_details(nhs_number)
        if patient:
            imms = self.immunisation_repo.create_immunization(immunization)
            return Immunization.parse_obj(imms)
        else:
            raise InvalidPatientId(nhs_number=nhs_number)

    def delete_immunization(self, imms_id) -> Immunization:
        """Delete an Immunization if it exits and return the ID back if successful.
        Exception will be raised if resource didn't exit. Multiple calls to this method won't change the
        record in the database.
        """
        imms = self.immunisation_repo.delete_immunization(imms_id)
        return Immunization.parse_obj(imms)

    def search_immunizations(self, nhs_number: str, disease_type: str):
        """find all instances of Immunization(s) for a patient and specified disease type.
        Returns List[Immunization]
        """
        # TODO: is disease type a mandatory field? (I assumed it is)
        #  i.e. Should we provide a search option for getting Patient's entire imms history?
        resources = self.immunisation_repo.find_immunizations(nhs_number, disease_type)

        entries = [Immunization.parse_obj(imms) for imms in resources]
        return FhirList.construct(entry=entries)
