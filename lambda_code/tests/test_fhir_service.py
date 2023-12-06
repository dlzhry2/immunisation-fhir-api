import json
import os
import sys
import unittest
import uuid
from unittest.mock import create_autospec, MagicMock
from fhir.resources.immunization import Immunization

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_repository import ImmunisationRepository
from fhir_service import FhirService
from pds import PdsService


def _create_an_immunization(imms_id) -> Immunization:
    base_imms = {
        "resourceType": "Immunization",
        "id": imms_id,
        "identifier": [
            {
                "system": "https://supplierABC/ODSCode",
                "value": imms_id
            }
        ],
        "status": "completed",
        "occurrenceDateTime": "2020-12-14T10:08:15+00:00",
        "patient": {
            "reference": "urn:uuid:124fcb63-669c-4a3c-af2b-caf55de167ec",
            "type": "Patient",
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/nhs-number",
                "value": "9000000009"
            }
        },
        "vaccineCode": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "39114911000001105",
                "display": "some text"
            }]
        },
    }
    return Immunization.parse_obj(base_imms)


def _create_an_immunization_dict(imms_id):
    imms = _create_an_immunization(imms_id)
    # Convert FHIR OrderedDict to Dict by first converting it to json and then load it again
    return json.loads(imms.json())


class TestGetImmunization(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunisationRepository)
        self.fhir_service = FhirService(self.imms_repo)

    def test_get_immunization_by_id(self):
        """it should find an Immunization by id"""
        imms_id = "an-id"
        self.imms_repo.get_immunization_by_id.return_value = _create_an_immunization(imms_id).dict()

        # When
        act_imms = self.fhir_service.get_immunization_by_id(imms_id)

        # Then
        self.imms_repo.get_immunization_by_id.assert_called_once_with(imms_id)
        self.assertEqual(act_imms.id, imms_id)

    def test_immunization_not_found(self):
        """it should return None if Immunization doesn't exist"""
        imms_id = "none-existent-id"
        self.imms_repo.get_immunization_by_id.return_value = None

        # When
        act_imms = self.fhir_service.get_immunization_by_id(imms_id)

        # Then
        self.imms_repo.get_immunization_by_id.assert_called_once_with(imms_id)
        self.assertEqual(act_imms, None)


class TestCreateImmunization(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunisationRepository)
        self.fhir_service = FhirService(self.imms_repo)
        self.fhir_service.pds_service = create_autospec(PdsService)
        self.imms_id = str(uuid.uuid4())
        self.req_imms = _create_an_immunization_dict(self.imms_id)

    def test_create_immunization(self):
        """it should create Immunization""" 
        self.imms_repo.create_immunization.return_value = self.req_imms
        self.fhir_service.lookup_nhs_number = MagicMock(return_value=self.req_imms)

        stored_imms = self.fhir_service.create_immunization(self.req_imms)

        self.imms_repo.create_immunization.assert_called_once_with(self.req_imms)
        self.assertIsInstance(stored_imms, Immunization)

    def test_lookup_nhs_number(self):
        """it should use PDS to lookup NHS number"""
        self.imms_repo.create_immunization.return_value = self.req_imms
        
        self.fhir_service.create_immunization(self.req_imms)
        
        self.fhir_service.pds_service.get_patient_details.assert_called_once_with(self.req_imms['patient']['identifier']['value'])

    def test_lookup_nhs_number_not_found(self):
        self.fhir_service.lookup_nhs_number = MagicMock(return_value=None)
        
        with self.assertRaises(Exception) as context:
            self.fhir_service.create_immunization(self.req_imms)
        
        self.assertIn('nhs number is not provided or is invalid', str(context.exception))
        self.fhir_service.pds_service.get_patient_details.assert_not_called()


class TestDeleteImmunization(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunisationRepository)
        self.fhir_service = FhirService(self.imms_repo)

    def test_delete_immunization(self):
        """it should delete Immunization record"""
        imms_id = "an-id"
        imms = json.loads(_create_an_immunization(imms_id).json())
        self.imms_repo.delete_immunization.return_value = imms

        # When
        act_imms = self.fhir_service.delete_immunization(imms_id)

        # Then
        self.imms_repo.delete_immunization.assert_called_once_with(imms_id)
        self.assertIsInstance(act_imms, Immunization)
        self.assertEqual(act_imms.id, imms_id)