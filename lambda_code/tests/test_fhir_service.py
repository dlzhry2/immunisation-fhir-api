import json
import unittest
from unittest.mock import create_autospec
import os
from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.list import List as FhirList
from fhir_repository import ImmunizationRepository
from fhir_service import FhirService, UpdateOutcome
from models.errors import (
    InvalidPatientId,
    CoarseValidationError,
    ResourceNotFoundError,
    InconsistentIdError,
)
from models.fhir_immunization import ImmunizationValidator
from pds_service import PdsService
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from decimal import Decimal

valid_nhs_number = "2374658346"


def _create_an_immunization(imms_id, nhs_number=valid_nhs_number) -> Immunization:
    base_imms = {
        "resourceType": "Immunization",
        "id": imms_id,
        "contained": [
            {
                "resourceType": "Practitioner",
                "id": "Pract1",
                "identifier": [
                    {
                        "system": "https://fhir.hl7.org.uk/Id/nmc-number",
                        "value": "99A9999A",
                    }
                ],
                "name": [{"family": "Nightingale", "given": ["Florence"]}],
            },
            {
                "resourceType": "Patient",
                "id": "Pat1",
                "identifier": [
                    {
                        "extension": [
                            {
                                "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                                "valueCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland",
                                            "code": "01",
                                            "display": "Number present and verified",
                                        }
                                    ]
                                },
                            }
                        ],
                        "system": "https://fhir.nhs.uk/Id/nhs-number",
                        "value": nhs_number,
                    }
                ],
                "name": [{"family": "Taylor", "given": ["Sarah"]}],
                "gender": "unknown",
                "birthDate": "1965-02-28",
                "address": [{"postalCode": "EC1A 1BB"}],
            },
            {
                "resourceType": "QuestionnaireResponse",
                "id": "QR1",
                "status": "completed",
                "item": [
                    {
                        "linkId": "Immunisation",
                        "answer": [{"valueReference": {"reference": "#"}}],
                    },
                    {
                        "linkId": "Consent",
                        "answer": [
                            {
                                "valueCoding": {
                                    "code": "310375005",
                                    "system": "http://snomed.info/sct",
                                    "display": "Immunization consent given (finding)",
                                }
                            }
                        ],
                    },
                    {
                        "linkId": "CareSetting",
                        "answer": [
                            {
                                "valueCoding": {
                                    "code": "413294000",
                                    "system": "http://snomed.info/sct",
                                    "display": "Community health services (qualifier value)",
                                }
                            }
                        ],
                    },
                    {"linkId": "ReduceValidation", "answer": [{"valueBoolean": False}]},
                    {
                        "linkId": "LocalPatient",
                        "answer": [
                            {
                                "valueReference": {
                                    "identifier": {
                                        "system": "https://ACME/identifiers/patient",
                                        "value": "ACME-patient123456",
                                    }
                                }
                            }
                        ],
                    },
                    {"linkId": "IpAddress", "answer": [{"valueString": "IP_ADDRESS"}]},
                    {"linkId": "UserId", "answer": [{"valueString": "USER_ID"}]},
                    {"linkId": "UserName", "answer": [{"valueString": "USER_NAME"}]},
                    {
                        "linkId": "SubmittedTimeStamp",
                        "answer": [{"valueDateTime": "2021-02-07T13:44:07+00:00"}],
                    },
                    {"linkId": "UserEmail", "answer": [{"valueString": "USER_EMAIL"}]},
                    {
                        "linkId": "PerformerSDSJobRole",
                        "answer": [{"valueString": "Specialist Nurse Practitioner"}],
                    },
                ],
            },
        ],
        "extension": [
            {
                "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "1324681000000101",
                            "display": "Administration of first dose of severe acute respiratory syndrome coronavirus 2 vaccine (procedure)",
                        }
                    ]
                },
            }
        ],
        "identifier": [
            {
                "system": "https://supplierABC/identifiers/vacc",
                "value": "ACME-vacc123456",
            }
        ],
        "status": "completed",
        "vaccineCode": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "39114911000001105",
                    "display": "COVID-19 Vaccine Vaxzevria (ChAdOx1 S [recombinant]) not less than 2.5x100,000,000 infectious units/0.5ml dose suspension for injection multidose vials (AstraZeneca UK Ltd) (product)",
                }
            ]
        },
        "patient": {"reference": "#Pat1"},
        "occurrenceDateTime": "2021-02-07T13:28:17.271+00:00",
        "recorded": "2021-02-07",
        "primarySource": True,
        "reportOrigin": {"text": "X99999"},
        "manufacturer": {"display": "AstraZeneca Ltd"},
        "location": {
            "identifier": {
                "value": "X99999",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            }
        },
        "lotNumber": "4120Z001",
        "expirationDate": "2021-07-02",
        "site": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "368208006",
                    "display": "Left upper arm structure (body structure)",
                }
            ]
        },
        "route": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "78421000",
                    "display": "Intramuscular route (qualifier value)",
                }
            ]
        },
        "doseQuantity": {
            "value": Decimal("0.5"),
            "unit": "milliliter",
            "system": "http://unitsofmeasure.org",
            "code": "ml",
        },
        "performer": [
            {"actor": {"reference": "#Pract1"}},
            {
                "actor": {
                    "type": "Organization",
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "B0C4P",
                    },
                    "display": "Acme Healthcare",
                }
            },
        ],
        "reasonCode": [
            {
                "coding": [
                    {
                        "code": "443684005",
                        "system": "http://snomed.info/sct",
                        "display": "Disease outbreak (event)",
                    }
                ]
            }
        ],
        "protocolApplied": [{"doseNumberPositiveInt": 1}],
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
        self.fhir_service = FhirService(
            self.imms_repo, self.pds_service, self.validator
        )

    def test_get_immunization_by_id(self):
        """it should find an Immunization by id"""
        imms_id = "an-id"
        self.imms_repo.get_immunization_by_id.return_value = _create_an_immunization(
            imms_id
        ).dict()
        self.pds_service.get_patient_details.return_value = {}

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

    # def test_get_immunization_by_id_patient_restricted(self):
    #     """it should return a filtered Immunization when patient is restricted"""
    #     imms_id = "restricted_id"
    #     with open(
    #         f"{os.path.dirname(os.path.abspath(__file__))}/sample_data/sample_immunization_event.json",
    #         "r",
    #     ) as immunization_data_file:
    #         immunization_data = json.load(immunization_data_file)
    #     with open(
    #         f"{os.path.dirname(os.path.abspath(__file__))}/sample_data/filtered_sample_immunization_event.json",
    #         "r",
    #     ) as filtered_immunization_data_file:
    #         filtered_immunization = json.load(filtered_immunization_data_file)
    #     self.imms_repo.get_immunization_by_id.return_value = immunization_data
    #     patient_data = {"meta": {"security": [{"code": "R"}]}}
    #     self.fhir_service.pds_service.get_patient_details.return_value = patient_data

    #     # When
    #     act_res = self.fhir_service.get_immunization_by_id(imms_id)

    #     # Then
    #     self.assertEqual(act_res, Immunization.parse_obj(filtered_immunization))


class TestCreateImmunization(unittest.TestCase):
    def setUp(self):
        self.imms_repo = create_autospec(ImmunizationRepository)
        self.pds_service = create_autospec(PdsService)
        self.validator = create_autospec(ImmunizationValidator)
        self.fhir_service = FhirService(
            self.imms_repo, self.pds_service, self.validator
        )

    def test_create_immunization(self):
        """it should create Immunization and validate it"""
        imms_id = "an-id"
        self.imms_repo.create_immunization.return_value = _create_an_immunization_dict(
            imms_id
        )
        pds_patient = {"id": "a-patient-id"}
        self.fhir_service.pds_service.get_patient_details.return_value = pds_patient

        nhs_number = valid_nhs_number
        req_imms = _create_an_immunization_dict(imms_id, nhs_number)

        # When
        stored_imms = self.fhir_service.create_immunization(req_imms)

        # Then
        self.imms_repo.create_immunization.assert_called_once_with(
            req_imms, pds_patient
        )
        self.validator.validate.assert_called_once_with(req_imms)
        self.fhir_service.pds_service.get_patient_details.assert_called_once_with(
            nhs_number
        )
        self.assertIsInstance(stored_imms, Immunization)

    def test_pre_validation_failed(self):
        """it should throw exception if Immunization is not valid"""
        self.imms_repo.create_immunization.return_value = _create_an_immunization_dict(
            "an-id"
        )
        validation_error = ValidationError(
            [
                ErrorWrapper(TypeError("bad type"), "/type"),
            ],
            Immunization,
        )
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
        self.fhir_service = FhirService(
            self.imms_repo, self.pds_service, self.validator
        )

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
        self.imms_repo.update_immunization.assert_called_once_with(
            imms_id, req_imms, pds_patient
        )
        self.fhir_service.pds_service.get_patient_details.assert_called_once_with(
            nhs_number
        )

    def test_none_existing_imms(self):
        """it should create a new record, if it doesn't exist"""
        imms_id = "an-id"
        imms = _create_an_immunization_dict(imms_id, valid_nhs_number)

        self.imms_repo.update_immunization.side_effect = ResourceNotFoundError(
            "Immunization", imms_id
        )
        self.fhir_service.pds_service.get_patient_details.return_value = {
            "id": "a-patient-id"
        }

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

        validation_error = ValidationError(
            [
                ErrorWrapper(TypeError("bad type"), "/type"),
            ],
            Immunization,
        )
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
        self.fhir_service.pds_service.get_patient_details.return_value = {
            "id": "patient-id"
        }

        req_imms = _create_an_immunization_dict("we-will-remove-this-id")
        del req_imms["id"]

        # When
        self.fhir_service.update_immunization(req_imms_id, req_imms)

        # Then
        passed_imms = self.imms_repo.update_immunization.call_args.args[1]
        self.assertEqual(passed_imms["id"], req_imms_id)

    def test_consistent_imms_id(self):
        """Immunization[id] should be the same as request"""
        req_imms_id = "an-id"
        self.imms_repo.update_immunization.return_value = None
        self.fhir_service.pds_service.get_patient_details.return_value = {
            "id": "patient-id"
        }

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
        self.fhir_service = FhirService(
            self.imms_repo, self.pds_service, self.validator
        )

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
        self.fhir_service = FhirService(
            self.imms_repo, self.pds_service, self.validator
        )

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
        self.imms_repo.find_immunizations.assert_called_once_with(
            nhs_number, disease_code
        )

    def test_make_fhir_list_from_search_result(self):
        """it should return a FHIR:List[Immunization] resource"""
        imms_ids = ["imms-1", "imms-2"]
        imms_list = [_create_an_immunization_dict(imms_id) for imms_id in imms_ids]
        self.imms_repo.find_immunizations.return_value = imms_list
        self.pds_service.get_patient_details.return_value = {}

        # When
        result = self.fhir_service.search_immunizations("an-id", "a-code")

        # Then
        self.assertIsInstance(result, FhirList)
        self.assertListEqual([entry.id for entry in result.entry], imms_ids)
