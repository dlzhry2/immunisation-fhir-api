from enum import Enum
from typing import Optional

from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.list import List as FhirList
from pydantic import ValidationError

from fhir_repository import ImmunizationRepository
from models.errors import (
    InvalidPatientId,
    CoarseValidationError,
    ResourceNotFoundError,
    InconsistentIdError,
)
from models.fhir_immunization import ImmunizationValidator
from pds_service import PdsService
from s_flag_handler import handle_s_flag


class UpdateOutcome(Enum):
    UPDATE = 0
    CREATE = 1


class FhirService:
    def __init__(
        self,
        imms_repo: ImmunizationRepository,
        pds_service: PdsService,
        pre_validator: ImmunizationValidator = ImmunizationValidator(
            add_post_validators=False
        ),
    ):
        self.immunization_repo = imms_repo
        self.pds_service = pds_service
        self.pre_validator = pre_validator

    def get_immunization_by_id(self, imms_id: str) -> Optional[Immunization]:
        imms = self.immunization_repo.get_immunization_by_id(imms_id)

        if not imms:
            return None

        nhs_number = [
            x for x in imms["contained"] if x.get("resourceType") == "Patient"
        ][0]["identifier"][0]["value"]
        patient = self.pds_service.get_patient_details(nhs_number)
        filtered_immunization = handle_s_flag(imms, patient)
        return Immunization.parse_obj(filtered_immunization)

    def create_immunization(self, immunization: dict) -> Immunization:
        try:
            self.pre_validator.validate(immunization)
        except ValidationError as error:
            raise CoarseValidationError(message=str(error))

        patient = self._validate_patient(immunization)
        imms = self.immunization_repo.create_immunization(immunization, patient)

        return Immunization.parse_obj(imms)

    def update_immunization(self, imms_id: str, immunization: dict) -> UpdateOutcome:
        if immunization.get("id", imms_id) != imms_id:
            raise InconsistentIdError(imms_id=imms_id)
        immunization["id"] = imms_id

        try:
            self.pre_validator.validate(immunization)
        except ValidationError as error:
            raise CoarseValidationError(message=str(error))

        patient = self._validate_patient(immunization)

        try:
            self.immunization_repo.update_immunization(imms_id, immunization, patient)
            return UpdateOutcome.UPDATE
        except ResourceNotFoundError:
            self.immunization_repo.create_immunization(immunization, patient)
            return UpdateOutcome.CREATE

    def delete_immunization(self, imms_id) -> Immunization:
        """Delete an Immunization if it exits and return the ID back if successful.
        Exception will be raised if resource didn't exit. Multiple calls to this method won't change the
        record in the database.
        """
        imms = self.immunization_repo.delete_immunization(imms_id)
        return Immunization.parse_obj(imms)

    def search_immunizations(self, nhs_number: str, disease_type: str) -> FhirList:
        """find all instances of Immunization(s) for a patient and specified disease type.
        Returns List[Immunization]
        """
        # TODO: is disease type a mandatory field? (I assumed it is)
        #  i.e. Should we provide a search option for getting Patient's entire imms history?
        resources = self.immunization_repo.find_immunizations(nhs_number, disease_type)

        patient = self.pds_service.get_patient_details(nhs_number)

        entries = [
            Immunization.parse_obj(handle_s_flag(imms, patient)) for imms in resources
        ]
        return FhirList.construct(entry=entries)

    def _validate_patient(self, imms: dict):
        nhs_number = [
            x for x in imms["contained"] if x.get("resourceType") == "Patient"
        ][0]["identifier"][0]["value"]
        patient = self.pds_service.get_patient_details(nhs_number)
        if patient:
            return patient
        else:
            raise InvalidPatientId(nhs_number=nhs_number)
