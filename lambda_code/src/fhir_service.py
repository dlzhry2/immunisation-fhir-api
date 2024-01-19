from typing import Optional

from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.list import List as FhirList
from pydantic import ValidationError

from fhir_repository import ImmunizationRepository
from models.errors import InvalidPatientId, CoarseValidationError
from models.fhir_immunization import ImmunizationValidator
from pds_service import PdsService
from s_flag_handler import remove_personal_info


class FhirService:
    def __init__(self, imms_repo: ImmunizationRepository, pds_service: PdsService,
                 pre_validator: ImmunizationValidator = ImmunizationValidator()):
        self.immunization_repo = imms_repo
        self.pds_service = pds_service
        self.pre_validator = pre_validator
        self.pre_validator.add_custom_root_validators()

    def get_immunization_by_id(self, imms_id: str) -> Optional[Immunization]:
        imms = self.immunization_repo.get_immunization_by_id(imms_id)

        if not imms:
            return None

        bundle = False if imms['resourceType'] == "Immunization" else True

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
        try:
            self.pre_validator.validate(immunization)
        except ValidationError as error:
            raise CoarseValidationError(message=str(error))

        # TODO: check if nhs number exists
        nhs_number = immunization['patient']['identifier']['value']
        patient = self.pds_service.get_patient_details(nhs_number)
        if patient:
            imms = self.immunization_repo.create_immunization(immunization, patient)
            return Immunization.parse_obj(imms)
        else:
            raise InvalidPatientId(nhs_number=nhs_number)

    def delete_immunization(self, imms_id) -> Immunization:
        """Delete an Immunization if it exits and return the ID back if successful.
        Exception will be raised if resource didn't exit. Multiple calls to this method won't change the
        record in the database.
        """
        imms = self.immunization_repo.delete_immunization(imms_id)
        return Immunization.parse_obj(imms)

    def search_immunizations(self, nhs_number: str, disease_type: str):
        """find all instances of Immunization(s) for a patient and specified disease type.
        Returns List[Immunization]
        """
        # TODO: is disease type a mandatory field? (I assumed it is)
        #  i.e. Should we provide a search option for getting Patient's entire imms history?
        resources = self.immunization_repo.find_immunizations(nhs_number, disease_type)

        entries = [Immunization.parse_obj(imms) for imms in resources]
        return FhirList.construct(entry=entries)
