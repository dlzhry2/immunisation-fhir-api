import os
import sys
import unittest
from unittest.mock import create_autospec

from fhir.resources.immunization import Immunization

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_repository import ImmunisationRepository
from fhir_service import FhirService


class TestFhirService(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunisationRepository)
        self.fhir_service = FhirService(self.imms_repo)

    def test_get_immunization_by_id(self):
        """it should find an Immunization by id"""
        imms_id = "a-id"

        self.imms_repo.get_immunization_by_id.return_value = self._create_an_immunization_obj(imms_id).dict()

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

    def test_delete_immunization(self):
        """it should delete Immunization record"""
        imms_id = "an-id"
        self.imms_repo.delete_immunization.return_value = imms_id

        # When
        act_imms = self.fhir_service.delete_immunization(imms_id)

        # Then
        self.imms_repo.delete_immunization.assert_called_once_with(imms_id)
        self.assertEqual(act_imms, imms_id)

    def test_delete_immunization_not_found(self):
        """it should return None when the ID doesn't exist"""
        imms_id = "a-non-existent-id"
        self.imms_repo.delete_immunization.return_value = None

        # When
        act_imms = self.fhir_service.delete_immunization(imms_id)

        # Then
        self.imms_repo.delete_immunization.assert_called_once_with(imms_id)
        self.assertEqual(act_imms, imms_id)

    @staticmethod
    def _create_an_immunization_obj(imms_id) -> Immunization:
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
