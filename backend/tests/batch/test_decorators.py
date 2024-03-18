from collections import OrderedDict

import copy
import unittest
from unittest.mock import ANY

from batch.decorators import decorate_patient, decorate_vaccination, decorate_vaccine, decorate_practitioner, \
    decorate_questionare
from mappings import vaccination_procedure_snomed_codes

"""Test each decorator in the transformer module
Each decorator has its own test class. Each method is used to test a specific scenario. For example there may be
different ways to create a patient object. We may need to handle legacy data, or Point of Care data that's different
from other PoCs. This means the decorator should be flexible enough to handle different scenarios. Hence a test class.
"""

raw_imms = {
    "resourceType": "Immunization",
    "contained": [],
    "extension": [],
    "performer": [],
}


class TestPatientDecorator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

    def test_add_patient(self):
        """it should add the patient object to the contained list"""
        # Given
        headers = OrderedDict([])

        decorate_patient(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["patient"] = {"reference": "#patient_1"}
        expected_imms["contained"].append({
            "resourceType": "Patient",
            "id": "patient_1",
            "identifier": [],
            "name": []
        })

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_nhs_number(self):
        """it should add the nhs number to the patient object"""
        # Given
        headers = OrderedDict([("nhs_number", "a_nhs_number")])

        # When
        decorate_patient(self.imms, headers)

        # Then
        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["patient"] = ANY
        expected_imms["contained"].append({
            "resourceType": "Patient",
            "id": ANY,
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/nhs-number",
                    "value": "a_nhs_number"
                }
            ],
            "name": []
        })

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_nhs_number_extension(self):
        """it should add the nhs number to the patient object"""
        # Given
        headers = OrderedDict([
            ("nhs_number", "a_nhs_number"),
            ("nhs_number_status_indicator_code", "a_nhs_number_status_indicator_code"),
            ("nhs_number_status_indicator_description", "a_nhs_number_status_indicator_description"),
        ])

        # When
        decorate_patient(self.imms, headers)

        # Then
        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["patient"] = ANY
        expected_imms["contained"].append({
            "resourceType": "Patient",
            "id": ANY,
            "identifier": [{
                "system": ANY,
                "value": ANY,
                "extension": [{
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland",
                            "code": "a_nhs_number_status_indicator_code",
                            "display": "a_nhs_number_status_indicator_description"
                        }]
                    }
                }]
            }],
            "name": []
        })

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_name(self):
        """it should add the name to the patient object"""
        # Given
        headers = OrderedDict([
            ("person_surname", "a_person_surname"),
            ("person_forename", "a_person_forename"),
        ])

        # When
        decorate_patient(self.imms, headers)

        # Then
        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["patient"] = ANY
        expected_imms["contained"].append({
            "resourceType": "Patient",
            "id": "patient_1",
            "identifier": [],
            "name": [
                {
                    "family": "a_person_surname",
                    "given": ["a_person_forename"]
                }
            ]
        })

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_dob(self):
        """it should add the dob to the patient object"""
        headers = OrderedDict([("person_dob", "a_person_dob")])

        decorate_patient(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["patient"] = ANY
        expected_imms["contained"].append({
            "resourceType": "Patient",
            "id": ANY,
            "identifier": [],
            "name": [],
            "birthDate": "a_person_dob"
        })

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_gender(self):
        """it should add gender code"""
        headers = OrderedDict([("person_gender_code", "a_person_gender_code")])

        decorate_patient(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["patient"] = ANY
        expected_imms["contained"].append({
            "resourceType": "Patient",
            "id": ANY,
            "identifier": [],
            "name": [],
            "gender": "a_person_gender_code"
        })

        self.assertDictEqual(expected_imms, self.imms)


class TestVaccineDecorator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

    def test_vaccine_product(self):
        headers = OrderedDict([
            ("vaccine_product_code", "a_vaccine_product_code"),
            ("vaccine_product_term", "a_vaccine_product_term"),
        ])

        decorate_vaccine(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["vaccineCode"] = {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "a_vaccine_product_code",
                "display": "a_vaccine_product_term"
            }]
        }
        self.assertDictEqual(expected_imms, self.imms)

    def test_manufacturer(self):
        headers = OrderedDict([("vaccine_manufacturer", "a_vaccine_manufacturer")])

        decorate_vaccine(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["manufacturer"] = "a_vaccine_manufacturer"

        self.assertDictEqual(expected_imms, self.imms)

    def test_expiration(self):
        headers = OrderedDict([("expiry_date", "a_expiry_date")])

        decorate_vaccine(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["expirationDate"] = "a_expiry_date"

        self.assertDictEqual(expected_imms, self.imms)

    def test_lot_number(self):
        headers = OrderedDict([("batch_number", "a_batch_number")])

        decorate_vaccine(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["lotNumber"] = "a_batch_number"

        self.assertDictEqual(expected_imms, self.imms)


class TestVaccinationDecorator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

    def test_vaccination_procedure(self):
        """it should get the vaccination procedure code and term and add it to the extension list"""
        a_vaccination_procedure_code = "1324681000000101"
        headers = OrderedDict([
            ("vaccination_procedure_code", a_vaccination_procedure_code),
            ("vaccination_procedure_term", "a_vaccination_procedure_term"),
        ])

        decorate_vaccination(self.imms, headers)

        # Then
        vac_type = vaccination_procedure_snomed_codes.get(a_vaccination_procedure_code)
        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["extension"].append({
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedureCode",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-VaccinationProcedureCode",
                        "code": vac_type,
                        "display": "a_vaccination_procedure_term"
                    }
                ]
            }
        })

        self.assertDictEqual(expected_imms, self.imms)

    def test_occurrence_date_time(self):
        """it should convert and add the occurrence date time to the vaccination object"""
        headers = OrderedDict([("date_and_time", "20240221T171930")])

        decorate_vaccination(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["occurrenceDateTime"] = "2024-02-21T17:19:30+00:00"

        self.assertDictEqual(expected_imms, self.imms)

    def test_primary_source_false(self):
        """it should set the primary source by converting the string to a boolean"""
        headers = OrderedDict([("primary_source", "FALSE")])

        decorate_vaccination(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["primarySource"] = False
        self.assertDictEqual(expected_imms, self.imms)

    def test_primary_source_true(self):
        """it should set the primary source by converting the string to a boolean"""
        headers = OrderedDict([("primary_source", "TRUE")])

        decorate_vaccination(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["primarySource"] = True
        self.assertDictEqual(expected_imms, self.imms)

    def test_report_origin(self):
        """it should set the report origin"""
        headers = OrderedDict([("report_origin", "a_report_origin")])

        decorate_vaccination(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["reportOrigin"] = "a_report_origin"
        self.assertDictEqual(expected_imms, self.imms)

    def test_vaccination_site(self):
        """it should get the vaccination site code and term and add it to the site object"""
        headers = OrderedDict([
            ("site_of_vaccination_code", "a_site_of_vaccination_code"),
            ("site_of_vaccination_term", "a_site_of_vaccination_term"),
        ])

        decorate_vaccination(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["site"] = {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "a_site_of_vaccination_code",
                    "display": "a_site_of_vaccination_term"
                }
            ]
        }

        self.assertDictEqual(expected_imms, self.imms)

    def test_vaccination_route(self):
        """it should get the vaccination route code and term and add it to the route object"""
        headers = OrderedDict([
            ("route_of_vaccination_code", "a_route_of_vaccination_code"),
            ("route_of_vaccination_term", "a_route_of_vaccination_term"),
        ])

        decorate_vaccination(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["route"] = {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "a_route_of_vaccination_code",
                    "display": "a_route_of_vaccination_term"
                }
            ]
        }

        self.assertDictEqual(expected_imms, self.imms)

    def test_dose_quantity(self):
        """it should get the dose amount, unit code and term and add it to the doseQuantity object"""
        headers = OrderedDict([
            ("dose_amount", "a_dose_amount"),
            ("dose_unit_code", "a_dose_unit_code"),
            ("dose_unit_term", "a_dose_unit_term"),
        ])

        decorate_vaccination(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["doseQuantity"] = {
            "value": "a_dose_amount",
            "unit": "a_dose_unit_code",
            "system": "a_dose_unit_term"
        }

        self.assertDictEqual(expected_imms, self.imms)


class TestPractitionerDecorator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

    def test_add_practitioner(self):
        """it should add the practitioner object to the contained list and the performer list"""
        headers = OrderedDict([
            ("performing_professional_body_reg_code", "a_performing_professional_body_reg_code")
        ])

        decorate_practitioner(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["contained"].append({
            "resourceType": "Practitioner",
            "id": "practitioner_1",
            "identifier": ANY,
            "name": []
        })
        expected_imms["performer"].append({"actor": {"reference": "#practitioner_1"}})

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_practitioner_identifier(self):
        headers = OrderedDict([
            ("performing_professional_body_reg_code", "a_performing_professional_body_reg_code"),
            ("performing_professional_body_reg_uri", "a_performing_professional_body_reg_uri"),
        ])

        decorate_practitioner(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["contained"].append({
            "resourceType": "Practitioner",
            "id": ANY,
            "identifier": [{
                "system": "a_performing_professional_body_reg_uri",
                "value": "a_performing_professional_body_reg_code"
            }],
            "name": []
        })
        expected_imms["performer"].append(ANY)

        self.assertDictEqual(expected_imms, self.imms)

    def test_practitioner_name(self):
        """it should add practitioner name"""
        headers = OrderedDict([
            ("performing_professional_body_reg_code", "a_performing_professional_body_reg_code"),
            ("performing_professional_forename", "a_performing_professional_forename"),
            ("performing_professional_surname", "a_performing_professional_surname"),
        ])

        decorate_practitioner(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["contained"].append({
            "resourceType": "Practitioner",
            "id": ANY,
            "identifier": ANY,
            "name": [{
                "family": "a_performing_professional_surname",
                "given": ["a_performing_professional_forename"]
            }]
        })
        expected_imms["performer"].append(ANY)

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_organisation(self):
        """it should add the organisation where the vaccination was given"""
        headers = OrderedDict([
            ("location_code", "a_location_code"),
            ("location_code_type_uri", "a_location_code_type_uri"),
        ])

        decorate_practitioner(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        # TODO: check source code TODO
        expected_imms["location"] = ANY

        expected_imms["performer"].append({
            "actor": {
                "resourceType": "Organization",
                "identifier": [{
                    "system": "a_location_code_type_uri",
                    "value": "a_location_code"
                }]
            }
        })

        self.assertDictEqual(expected_imms, self.imms)

    def test_location(self):
        """it should get the location code and type and add it to the location object"""
        headers = OrderedDict([
            ("location_code", "a_location_code"),
            ("location_code_type_uri", "a_location_code_type_uri"),
        ])

        decorate_practitioner(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        # TODO: this is tested before and contains the same location. Check TODO in decorator source code
        expected_imms["performer"].append(ANY)
        expected_imms["location"] = {
            "identifier": {
                "value": "a_location_code",
                "system": "a_location_code_type_uri"
            }}

        self.assertDictEqual(expected_imms, self.imms)


class TestDecorateQuestionare(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

    @staticmethod
    def _make_questionare(imms: dict, name: str, item: dict):
        questionare = {
            "resourceType": "QuestionnaireResponse",
            "id": ANY,
            "status": ANY,
            "item": [{
                "linkId": name,
                "answer": [item]
            }]
        }
        imms["contained"].append(questionare)

    def test_add_consent(self):
        """it should add the consent to the questionare list"""
        headers = OrderedDict([
            ("consent_for_treatment_code", "a_consent_for_treatment_code"),
            ("consent_for_treatment_description", "a_consent_for_treatment_description"),
        ])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        item = {"valueCoding": {
            "system": "http://snomed.info/sct",
            "code": "a_consent_for_treatment_code",
            "display": "a_consent_for_treatment_description"
        }}
        self._make_questionare(expected_imms, "Consent", item)

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_care_setting(self):
        """it should add the care setting to the questionare list"""
        headers = OrderedDict([
            ("care_setting_type_code", "a_care_setting_type_code"),
            ("care_setting_type_description", "a_care_setting_type_description"),
        ])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        item = {"valueCoding": {
            "system": "http://snomed.info/sct",
            "code": "a_care_setting_type_code",
            "display": "a_care_setting_type_description"
        }}
        self._make_questionare(expected_imms, "CareSetting", item)

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_local_patient(self):
        """it should add the local patient to the questionare list"""
        headers = OrderedDict([
            ("local_patient_id", "a_local_patient_id"),
            ("local_patient_uri", "a_local_patient_uri"),
        ])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        item = {"valueReference": {
            "identifier": {
                "system": "a_local_patient_uri",
                "value": "a_local_patient_id"
            }
        }}
        self._make_questionare(expected_imms, "LocalPatient", item)

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_ip_address(self):
        """it should add the ip address to the questionare list"""
        headers = OrderedDict([("ip_address", "a_ip_address")])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        self._make_questionare(expected_imms, "IpAddress", {"valueString": "a_ip_address"})

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_user_id(self):
        """it should add the user id to the questionare list"""
        headers = OrderedDict([("user_id", "a_user_id")])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        self._make_questionare(expected_imms, "UserId", {"valueString": "a_user_id"})

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_user_name(self):
        """it should add the user name to the questionare list"""
        headers = OrderedDict([("user_name", "a_user_name")])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        self._make_questionare(expected_imms, "UserName", {"valueString": "a_user_name"})

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_user_email(self):
        """it should add the user email to the questionare list"""
        headers = OrderedDict([("user_email", "a_user_email")])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        self._make_questionare(expected_imms, "UserEmail", {"valueString": "a_user_email"})

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_submitted_timestamp(self):
        """it should convert and add the submitted timestamp to the questionare list"""
        headers = OrderedDict([("submitted_timestamp", "20240221T17193000")])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        self._make_questionare(expected_imms,
                               "SubmittedTimeStamp", {"valueDateTime": "2024-02-21T17:19:30+00:00"})

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_performer_job_role(self):
        """it should add the performer job role to the questionare list"""
        headers = OrderedDict([("sds_job_role_name", "a_sds_job_role_name")])

        decorate_questionare(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        self._make_questionare(expected_imms, "PerformerSDSJobRole", {"valueString": "a_sds_job_role_name"})

        self.assertDictEqual(expected_imms, self.imms)
