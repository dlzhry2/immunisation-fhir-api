import json
import unittest
from unittest.mock import create_autospec

from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.list import List as FhirList
from fhir_repository import ImmunizationRepository
from fhir_service import FhirService, UpdateOutcome
from models.errors import InvalidPatientId, CoarseValidationError, ResourceNotFoundError, InconsistentIdError
from models.fhir_immunization import ImmunizationValidator
from pds_service import PdsService
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

valid_nhs_number = "2374658346"


def _create_an_immunization(imms_id, nhs_number=valid_nhs_number) -> Immunization:
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
                "value": nhs_number
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


def _create_an_immunization_dict(imms_id, nhs_number=valid_nhs_number):
    imms = _create_an_immunization(imms_id, nhs_number)
    # Convert FHIR OrderedDict to Dict by first converting it to json and then load it again
    return json.loads(imms.json())


class TestGetImmunization(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunizationRepository)
        self.pds_service = create_autospec(PdsService)
        self.validator = create_autospec(ImmunizationValidator)
        self.fhir_service = FhirService(self.imms_repo, self.pds_service, self.validator)

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
        self.imms_repo = create_autospec(ImmunizationRepository)
        self.pds_service = create_autospec(PdsService)
        self.validator = create_autospec(ImmunizationValidator)
        self.fhir_service = FhirService(self.imms_repo, self.pds_service, self.validator)

    def test_create_immunization(self):
        """it should create Immunization and validate it"""
        imms_id = "an-id"
        self.imms_repo.create_immunization.return_value = _create_an_immunization_dict(imms_id)
        pds_patient = {"id": "a-patient-id"}
        self.fhir_service.pds_service.get_patient_details.return_value = pds_patient

        nhs_number = valid_nhs_number
        req_imms = _create_an_immunization_dict(imms_id, nhs_number)

        # When
        stored_imms = self.fhir_service.create_immunization(req_imms)

        # Then
        self.imms_repo.create_immunization.assert_called_once_with(req_imms, pds_patient)
        self.validator.validate.assert_called_once_with(req_imms)
        self.fhir_service.pds_service.get_patient_details.assert_called_once_with(nhs_number)
        self.assertIsInstance(stored_imms, Immunization)

    def test_pre_validation_failed(self):
        """it should throw exception if Immunization is not valid"""
        self.imms_repo.create_immunization.return_value = _create_an_immunization_dict("an-id")
        validation_error = ValidationError([ErrorWrapper(TypeError('bad type'), '/type'), ], Immunization)
        self.validator.validate.side_effect = validation_error
        expected_msg = str(validation_error)

        with self.assertRaises(CoarseValidationError) as error:
            # When
            self.fhir_service.create_immunization({})

        # Then
        self.assertEqual(error.exception.message, expected_msg)
        self.imms_repo.create_immunization.assert_not_called()
        self.pds_service.get_patient_details.assert_not_called()

    def test_patient_error(self):
        """it should throw error when PDS can't resolve patient"""
        self.fhir_service.pds_service.get_patient_details.return_value = None
        invalid_nhs_number = "a-bad-patient-id"
        bad_patient_imms = _create_an_immunization_dict("an-id", invalid_nhs_number)

        with self.assertRaises(InvalidPatientId) as e:
            # When
            self.fhir_service.create_immunization(bad_patient_imms)

        # Then
        self.assertEqual(e.exception.nhs_number, invalid_nhs_number)
        self.imms_repo.create_immunization.assert_not_called()


class TestUpdateImmunization(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunizationRepository)
        self.pds_service = create_autospec(PdsService)
        self.validator = create_autospec(ImmunizationValidator)
        self.fhir_service = FhirService(self.imms_repo, self.pds_service, self.validator)

    def test_update_immunization(self):
        """it should update Immunization and validate NHS number"""
        imms_id = "an-id"
        self.imms_repo.update_immunization.return_value = None
        pds_patient = {"id": "a-patient-id"}
        self.fhir_service.pds_service.get_patient_details.return_value = pds_patient

        nhs_number = valid_nhs_number
        req_imms = _create_an_immunization_dict(imms_id, nhs_number)

        # When
        outcome = self.fhir_service.update_immunization(imms_id, req_imms)

        # Then
        self.assertEqual(outcome, UpdateOutcome.UPDATE)
        self.imms_repo.update_immunization.assert_called_once_with(imms_id, req_imms, pds_patient)
        self.fhir_service.pds_service.get_patient_details.assert_called_once_with(nhs_number)

    def test_none_existing_imms(self):
        """it should create a new record, if it doesn't exist"""
        imms_id = "an-id"
        imms = _create_an_immunization_dict(imms_id, valid_nhs_number)

        self.imms_repo.update_immunization.side_effect = ResourceNotFoundError("Immunization", imms_id)
        self.fhir_service.pds_service.get_patient_details.return_value = {"id": "a-patient-id"}

        # When
        outcome = self.fhir_service.update_immunization(imms_id, imms)

        # Then
        self.assertEqual(outcome, UpdateOutcome.CREATE)
        self.imms_repo.create_immunization.assert_called_once()

    def test_pre_validation_failed(self):
        """it should throw exception if Immunization is not valid"""
        imms_id = "an-id"
        imms = _create_an_immunization_dict(imms_id)
        imms["patient"] = {"identifier": {"value": valid_nhs_number}}

        self.imms_repo.update_immunization.return_value = {}

        validation_error = ValidationError([ErrorWrapper(TypeError('bad type'), '/type'), ], Immunization)
        self.validator.validate.side_effect = validation_error
        expected_msg = str(validation_error)

        with self.assertRaises(CoarseValidationError) as error:
            # When
            self.fhir_service.update_immunization("an-id", imms)

        # Then
        self.assertEqual(error.exception.message, expected_msg)
        self.imms_repo.update_immunization.assert_not_called()
        self.pds_service.get_patient_details.assert_not_called()

    def test_id_not_present(self):
        """it should populate id in the message if it is not present"""
        req_imms_id = "an-id"
        self.imms_repo.update_immunization.return_value = None
        self.fhir_service.pds_service.get_patient_details.return_value = {"id": "patient-id"}

        req_imms = _create_an_immunization_dict("we-will-remove-this-id")
        del req_imms['id']

        # When
        self.fhir_service.update_immunization(req_imms_id, req_imms)

        # Then
        passed_imms = self.imms_repo.update_immunization.call_args.args[1]
        self.assertEqual(passed_imms["id"], req_imms_id)

    def test_consistent_imms_id(self):
        """Immunization[id] should be the same as request"""
        req_imms_id = "an-id"
        self.imms_repo.update_immunization.return_value = None
        self.fhir_service.pds_service.get_patient_details.return_value = {"id": "patient-id"}

        obj_imms_id = "a-diff-id"
        req_imms = _create_an_immunization_dict(obj_imms_id)

        with self.assertRaises(InconsistentIdError) as error:
            # When
            self.fhir_service.update_immunization(req_imms_id, req_imms)

        # Then
        self.assertEqual(req_imms_id, error.exception.imms_id)
        self.imms_repo.update_immunization.assert_not_called()
        self.pds_service.get_patient_details.assert_not_called()

    def test_patient_error(self):
        """it should throw error when PDS can't resolve patient"""
        self.fhir_service.pds_service.get_patient_details.return_value = None
        imms_id = "an-id"
        invalid_nhs_number = "a-bad-patient-id"
        bad_patient_imms = _create_an_immunization_dict(imms_id, invalid_nhs_number)

        with self.assertRaises(InvalidPatientId) as e:
            # When
            self.fhir_service.update_immunization(imms_id, bad_patient_imms)

        # Then
        self.assertEqual(e.exception.nhs_number, invalid_nhs_number)
        self.imms_repo.update_immunization.assert_not_called()


class TestDeleteImmunization(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunizationRepository)
        self.pds_service = create_autospec(PdsService)
        self.validator = create_autospec(ImmunizationValidator)
        self.fhir_service = FhirService(self.imms_repo, self.pds_service, self.validator)

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


class TestSearchImmunizations(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunizationRepository)
        self.pds_service = create_autospec(PdsService)
        self.validator = create_autospec(ImmunizationValidator)
        self.fhir_service = FhirService(self.imms_repo, self.pds_service, self.validator)

    def test_map_disease_type_to_disease_code(self):
        """it should map disease_type to disease_code"""
        # TODO: for this ticket we are assuming code is provided
        nhs_number = "a-patient-id"
        disease_type = "a-disease-code"
        # TODO: here we are assuming disease_type=disease_code this is because the mapping is not in place yet
        disease_code = disease_type

        # When
        _ = self.fhir_service.search_immunizations(nhs_number, disease_code)

        # Then
        self.imms_repo.find_immunizations.assert_called_once_with(nhs_number, disease_code)

    def test_make_fhir_list_from_search_result(self):
        """it should return a FHIR:List[Immunization] resource"""
        imms_ids = ["imms-1", "imms-2"]
        imms_list = [_create_an_immunization_dict(imms_id) for imms_id in imms_ids]
        self.imms_repo.find_immunizations.return_value = imms_list

        # When
        result = self.fhir_service.search_immunizations("an-id", "a-code")

        # Then
        self.assertIsInstance(result, FhirList)
        self.assertListEqual([entry.id for entry in result.entry], imms_ids)
