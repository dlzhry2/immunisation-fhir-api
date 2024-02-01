from typing import Optional

from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.bundle import Bundle as FhirBundle
from fhir.resources.R4B.bundle import BundleEntry
from fhir.resources.R4B.bundle import BundleLink
from pydantic import ValidationError
import os
from fhir_repository import ImmunizationRepository
from models.errors import InvalidPatientId, CoarseValidationError
from models.fhir_immunization import ImmunizationValidator
from pds_service import PdsService


def get_service_url(
    service_env: str = os.getenv("IMMUNIZATION_ENV"),
    service_base_path: str = os.getenv("IMMUNIZATION_BASE_PATH"),
):
    non_prod = ["internal-dev", "int", "sandbox"]
    if service_env in non_prod:
        subdomain = f"{service_env}."
    if service_env == "prod":
        subdomain = ""
    else:
        subdomain = "internal-dev."
    return f"https://{subdomain}api.service.nhs.uk/{service_base_path}"


class FhirService:
    def __init__(
        self,
        imms_repo: ImmunizationRepository,
        pds_service: PdsService,
        pre_validator: ImmunizationValidator = ImmunizationValidator(),
    ):
        self.immunization_repo = imms_repo
        self.pds_service = pds_service
        self.pre_validator = pre_validator
        self.pre_validator.add_custom_root_validators()

    def get_immunization_by_id(self, imms_id: str) -> Optional[Immunization]:
        imms = self.immunization_repo.get_immunization_by_id(imms_id)
        if imms:
            # TODO: This shouldn't raise an exception since, we validate the message before storing it,
            #  but what if the stored message is different from the requested FHIR version?
            return Immunization.parse_obj(imms)
        else:
            return None

    def create_immunization(self, immunization: dict) -> Immunization:
        try:
            self.pre_validator.validate(immunization)
        except ValidationError as error:
            raise CoarseValidationError(message=str(error))

        # TODO: check if nhs number exists
        nhs_number = immunization["patient"]["identifier"]["value"]
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

        entries = [
            BundleEntry(resource=Immunization.parse_obj(imms)) for imms in resources
        ]
        fhir_bundle = FhirBundle(
            resourceType="Bundle",
            type="searchset",  # Set the type to "searchset"
            entry=entries,
        )
        url = f"{get_service_url()}/Immunization?patient={nhs_number}&diseaseType={disease_type}"
        fhir_bundle.link = [BundleLink(relation="self", url=url)]
        return fhir_bundle
