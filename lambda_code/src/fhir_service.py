from typing import Optional
from fhir.resources.immunization import Immunization
from fhir_repository import ImmunisationRepository
from models.errors import UnhandledResponseError
import boto3
from botocore.config import Config
from pds import PdsService, Authenticator


class FhirService:
    def __init__(self, imms_repo: ImmunisationRepository):
        self.immunisation_repo = imms_repo
        env = "internal-dev"
        my_config = Config(region_name = 'eu-west-2')
        self.pds_service = PdsService(Authenticator(boto3.client('secretsmanager', config=my_config), env), env)

    def get_immunization_by_id(self, imms_id: str) -> Optional[Immunization]:
        imms = self.immunisation_repo.get_immunization_by_id(imms_id)
        if imms:
            # TODO: This shouldn't raise an exception since, we validate the message before storing it,
            #  but what if the stored message is different from the requested FHIR version?
            return Immunization.parse_obj(imms)
        else:
            return None
        
    def lookup_nhs_number(self, immunization: dict):
        is_valid_patient = self.pds_service.get_patient_details(immunization['patient']['identifier']['value'])
        if is_valid_patient:
            return is_valid_patient
        return None

    def create_immunization(self, immunization: dict) -> Immunization:
        is_valid_patient = self.lookup_nhs_number(immunization)
        if is_valid_patient:
            imms = self.immunisation_repo.create_immunization(immunization)
            return Immunization.parse_obj(imms)
        else:
            raise Exception('nhs_number is not provided or is invalid')

    def delete_immunization(self, imms_id) -> Immunization:
        """Delete an Immunization if it exits and return the ID back if successful.
        Exception will be raised if resource didn't exit. Multiple calls to this method won't change the
        record in the database.
        """
        imms = self.immunisation_repo.delete_immunization(imms_id)
        return Immunization.parse_obj(imms)
