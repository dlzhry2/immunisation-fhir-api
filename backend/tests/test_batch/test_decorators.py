from collections import OrderedDict
from decimal import Decimal
import copy
import unittest
from unittest.mock import ANY, MagicMock, patch

from batch.decorators import (
    _decorate_patient,
    _decorate_vaccination,
    _decorate_vaccine,
    _decorate_performer,
    _decorate_questionare,
    decorate,
    _decorate_immunization,
)
from batch.errors import DecoratorError, TransformerFieldError, TransformerRowError, TransformerUnhandledError
from constants import valid_nhs_number, address_unknown_postcode

"""Test each decorator in the transformer module
Each decorator has its own test class. Each method is used to test a specific scenario. For example there may be
different ways to create a patient object. We may need to handle legacy data, or Point of Care data that's different
from other PoCs. This means the decorator should be flexible enough to handle different scenarios. Hence a test class.
NOTE: testing protected methods is not ideal. But in this case, we are testing the decorators in isolation.
NOTE: the public function `decorate` is tested in `TestDecorate` class.
"""

raw_imms: dict = {"resourceType": "Immunization", "contained": []}
vaccination_procedure_url = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure"
vaccination_situation_url = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation"
snomed_url = "http://snomed.info/sct"
nhs_number_verification_url = "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland"
base_extension_item = {"valueCodeableConcept": {"coding": [{"system": snomed_url}]}}

vaccination_procedure_extension_item = {
    "url": vaccination_procedure_url,
    "valueCodeableConcept": {
        "coding": [
            {
                "system": snomed_url,
                "code": "a_vaccination_procedure_code",
                "display": "a_vaccination_procedure_term",
            }
        ]
    },
}

vaccination_situation_extension_item = {
    "url": vaccination_situation_url,
    "valueCodeableConcept": {
        "coding": [
            {
                "system": snomed_url,
                "code": "a_vaccination_situation_code",
                "display": "a_vaccination_situation_term",
            }
        ]
    },
}

# vaccination_procedure_extension_item = {
#     "url": vaccination_procedure_url,
#     "valueCodeableConcept": {
#         "coding": [
#             {
#                 "system": nhs_number_verification_url,
#                 "code": "a_vaccination_procedure_code",
#                 "display": "a_vaccination_procedure_term",
#             }
#         ]
#     },
# }


class TestDecorate(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

        self.decorator0 = MagicMock(name="decorator0")
        self.decorator1 = MagicMock(name="decorator1")
        self.patcher = patch("batch.decorators.all_decorators", [self.decorator0, self.decorator1])
        self.patcher.start()

    def test_decorate_apply_decorators(self):
        """it should decorate the raw imms by applying the decorators"""

        # we create two mock decorators. Then we make sure they both contribute to the imms
        def decorator_0(_imms, _record):
            _imms["decorator_0"] = "decorator_0"
            return None

        def decorator_1(_imms, _record):
            _imms["decorator_1"] = "decorator_1"
            return None

        self.decorator0.side_effect = decorator_0
        self.decorator1.side_effect = decorator_1

        # When
        imms = {}
        decorate(imms, OrderedDict([]))

        # Then
        decorators_contribution = {
            "decorator_0": "decorator_0",
            "decorator_1": "decorator_1",
        }
        # initial imms is empty so, the contribution should be equal to the decorated imms
        self.assertEqual(imms, decorators_contribution)

    def test_accumulate_errors(self):
        """it should keep calling decorators and accumulate errors"""

        def decorator_0(_imms, _record):
            return DecoratorError(
                errors=[TransformerFieldError(message="field a and b failed", field="a")], decorator_name="decorator_0"
            )

        def decorator_1(_imms, _record):
            return DecoratorError(
                errors=[TransformerFieldError(message="field x failed", field="b")], decorator_name="decorator_1"
            )

        self.decorator0.side_effect = decorator_0
        self.decorator1.side_effect = decorator_1

        # When
        with self.assertRaises(TransformerRowError) as e:
            imms = {}
            decorate(imms, OrderedDict([]))

        # Then
        self.assertEqual(len(e.exception.errors), 2)

    def test_unhandled_error(self):
        """it should raise an error if a decorator throws an error"""

        def decorator_0(_imms, _record):
            raise ValueError("decorator_0")

        def decorator_1(_imms, _record):
            return None

        self.decorator0.side_effect = decorator_0
        self.decorator1.side_effect = decorator_1

        # When
        with self.assertRaises(TransformerUnhandledError) as e:
            imms = {}
            decorate(imms, OrderedDict([]))

        # Then
        self.assertEqual(e.exception.decorator_name, str(self.decorator0))
        self.decorator1.assert_not_called()


class TestImmunizationDecorator(unittest.TestCase):
    def setUp(self):
        self.imms = copy.deepcopy(raw_imms)
        self.completed_all_headers = OrderedDict(
            [
                ("not_given", "false"),
                ("action_flag", "new"),
                ("indication_code", "INDICATION_CODE"),
                ("indication_term", "indication term"),
                ("recorded_date", "20000101"),
                ("unique_id", "UNIQUE_ID_123"),
                ("unique_id_uri", "unique_id_uri"),
            ]
        )
        self.not_done_all_headers = OrderedDict(
            [
                ("not_given", "true"),
                ("action_flag", "new"),
                ("reason_not_given_code", "REASON_NOT_GIVEN_CODE"),
                ("reason_not_given_term", "reason not given term"),
                ("recorded_date", "20000101"),
                ("unique_id", "UNIQUE_ID_123"),
                ("unique_id_uri", "unique_id_uri"),
            ]
        )

    def test_completed_all_headers(self):
        _decorate_immunization(self.imms, self.completed_all_headers)

        expected_output = {
            "resourceType": "Immunization",
            "contained": [],
            "status": "completed",
            "reasonCode": [{"coding": [{"code": "INDICATION_CODE", "display": "indication term"}]}],
            "recorded": "2000-01-01",
            "identifier": [{"system": "unique_id_uri", "value": "UNIQUE_ID_123"}],
        }

        self.assertDictEqual(self.imms, expected_output)

    def test_not_done_all_headers(self):
        _decorate_immunization(self.imms, self.not_done_all_headers)

        expected_output = {
            "resourceType": "Immunization",
            "contained": [],
            "status": "not-done",
            "statusReason": {"coding": [{"code": "REASON_NOT_GIVEN_CODE", "display": "reason not given term"}]},
            "recorded": "2000-01-01",
            "identifier": [{"system": "unique_id_uri", "value": "UNIQUE_ID_123"}],
        }

        self.assertDictEqual(self.imms, expected_output)

    def test_no_headers(self):
        _decorate_immunization(self.imms, OrderedDict([]))
        self.assertDictEqual(self.imms, {"resourceType": "Immunization", "contained": []})

    def test_not_given_and_action_flag_true(self):
        """Test status is set to the appropriate value based on not_given and action_flag"""
        for not_given, action_flag, status in [
            ("true", "new", "not-done"),
            ("TRUE", "UPDATE", "not-done"),
            ("fAlsE", "nEw", "completed"),
            ("false", "update", "completed"),
        ]:
            _decorate_immunization(self.imms, OrderedDict([("not_given", not_given), ("action_flag", action_flag)]))
            self.assertEqual(status, self.imms["status"])

            # TODO: Test invalid values of not_given and action_flag

    def test_reason_not_given(self):
        """it should add the reason why the vaccine was not given"""
        # Code and term both non-empty
        headers = OrderedDict(
            [("reason_not_given_code", "a_not_given_reason_code"), ("reason_not_given_term", "a_not_given_reason_term")]
        )
        _decorate_immunization(self.imms, headers)
        expected = {"coding": [{"code": "a_not_given_reason_code", "display": "a_not_given_reason_term"}]}
        self.assertDictEqual(expected, self.imms["statusReason"])

        # Code non-empty, term empty
        headers = OrderedDict([("reason_not_given_code", "a_not_given_reason_code")])
        _decorate_immunization(self.imms, headers)
        expected = {"coding": [{"code": "a_not_given_reason_code"}]}
        self.assertDictEqual(expected, self.imms["statusReason"])

        # Code empty, term non-empty
        headers = OrderedDict([("reason_not_given_term", "a_not_given_reason_term")])
        _decorate_immunization(self.imms, headers)
        expected = {"coding": [{"display": "a_not_given_reason_term"}]}
        self.assertDictEqual(expected, self.imms["statusReason"])

    def test_indication(self):
        """it should add the reason why the vaccine was given"""
        # Code and term both non-empty
        headers = OrderedDict([("indication_code", "indication_code"), ("indication_term", "indication_term")])
        _decorate_immunization(self.imms, headers)
        expected = [{"coding": [{"code": "indication_code", "display": "indication_term"}]}]
        self.assertListEqual(expected, self.imms["reasonCode"])

        # Code non-empty, term empty
        headers = OrderedDict([("indication_code", "indication_code")])
        _decorate_immunization(self.imms, headers)
        expected = [{"coding": [{"code": "indication_code"}]}]
        self.assertListEqual(expected, self.imms["reasonCode"])

        # Code empty, term non-empty
        headers = OrderedDict([("indication_term", "indication_term"), ("indication_code", "")])
        _decorate_immunization(self.imms, headers)
        expected = [{"coding": [{"display": "indication_term"}]}]
        self.assertListEqual(expected, self.imms["reasonCode"])

    def test_recorded_date(self):
        """it should convert and add the recorded date to the immunization object"""
        _decorate_immunization(self.imms, OrderedDict([("recorded_date", "20240221")]))
        self.assertEqual("2024-02-21", self.imms["recorded"])

    def test_identifier(self):
        """it should add unique id as identifier"""
        # id and uri non-empty
        _decorate_immunization(
            self.imms, OrderedDict([("unique_id", "a_unique_id"), ("unique_id_uri", "a_unique_id_uri")])
        )
        self.assertListEqual([{"value": "a_unique_id", "system": "a_unique_id_uri"}], self.imms["identifier"])

        # id non-empty, uri empty
        _decorate_immunization(self.imms, OrderedDict([("unique_id", "a_unique_id"), ("unique_id_uri", None)]))
        self.assertListEqual([{"value": "a_unique_id"}], self.imms["identifier"])

        # id empty, uri non-empty
        _decorate_immunization(self.imms, OrderedDict([("unique_id_uri", "a_unique_id_uri")]))
        self.assertListEqual([{"system": "a_unique_id_uri"}], self.imms["identifier"])


class TestPatientDecorator(unittest.TestCase):
    """Tests for _decorate_patient"""

    def setUp(self):
        self.imms = copy.deepcopy(raw_imms)

    def test_all_patient_headers(self):
        """Test that all patient fields are added when all patient fields contain non-empty data"""
        all_patient_headers = OrderedDict(
            [
                ("person_surname", "surname"),
                ("person_forename", "forename"),
                ("person_gender_code", "1"),
                ("person_dob", "20000101"),
                ("person_postcode", address_unknown_postcode),
                ("nhs_number", valid_nhs_number),
                ("nhs_number_status_indicator_code", "an_nhs_status_code"),
                ("nhs_number_status_indicator_description", "an_nhs_status_description"),
            ]
        )
        _decorate_patient(self.imms, all_patient_headers)

        expected_output = {
            "resourceType": "Immunization",
            "contained": [
                {
                    "resourceType": "Patient",
                    "id": "Patient1",
                    "identifier": [
                        {
                            "extension": [
                                {
                                    "url": "https://fhir.hl7.org.uk/StructureDefinition/"
                                    + "Extension-UKCore-NHSNumberVerificationStatus",
                                    "valueCodeableConcept": {
                                        "coding": [
                                            {
                                                "system": "https://fhir.hl7.org.uk/CodeSystem/"
                                                + "UKCore-NHSNumberVerificationStatusEngland",
                                                "code": "an_nhs_status_code",
                                                "display": "an_nhs_status_description",
                                            }
                                        ]
                                    },
                                }
                            ],
                            "system": "https://fhir.nhs.uk/Id/nhs-number",
                            "value": valid_nhs_number,
                        }
                    ],
                    "name": [{"family": "surname", "given": ["forename"]}],
                    "gender": "male",
                    "birthDate": "2000-01-01",
                    "address": [{"postalCode": address_unknown_postcode}],
                },
            ],
            "patient": {"reference": "#Patient1"},
        }

        self.assertDictEqual(self.imms, expected_output)

    def test_no_headers(self):
        """Test that no fields are added when no patient fields contain non-empty data"""
        _decorate_patient(self.imms, OrderedDict([]))
        self.assertDictEqual(self.imms, {"resourceType": "Immunization", "contained": []})

    def test_dob(self):
        """it should convert and add the dob to the patient object"""
        _decorate_patient(self.imms, OrderedDict([("person_dob", "19930821")]))
        expected_imms = {
            "resourceType": "Immunization",
            "contained": [{"resourceType": "Patient", "id": "Patient1", "birthDate": "1993-08-21"}],
            "patient": {"reference": "#Patient1"},
        }
        self.assertDictEqual(expected_imms, self.imms)

    def test_gender_code(self):
        """it should convert gender code to fhir code and leave it as is if we can't convert it"""
        imms = copy.deepcopy(self.imms)
        _decorate_patient(imms, OrderedDict([("person_gender_code", "1")]))
        expected_contained_patient = {"resourceType": "Patient", "id": "Patient1", "gender": "male"}
        self.assertDictEqual(expected_contained_patient, imms["contained"][0])

        imms = copy.deepcopy(self.imms)
        _decorate_patient(imms, OrderedDict([("person_gender_code", "invalid_code")]))
        expected_contained_patient = {"resourceType": "Patient", "id": "Patient1", "gender": "invalid_code"}
        self.assertDictEqual(expected_contained_patient, imms["contained"][0])

    def test_address(self):
        """it should add postcode and address to the patient object"""
        _decorate_patient(self.imms, OrderedDict([("person_postcode", "a_person_postcode")]))
        expected_contained_patient = {
            "resourceType": "Patient",
            "id": "Patient1",
            "address": [{"postalCode": "a_person_postcode"}],
        }
        self.assertDictEqual(expected_contained_patient, self.imms["contained"][0])

    def test_add_name(self):
        """it should add the name to the patient object"""
        # Surname and forename non-empty
        imms = copy.deepcopy(self.imms)
        _decorate_patient(imms, OrderedDict([("person_surname", "a_surname"), ("person_forename", "a_forename")]))
        self.assertListEqual([{"family": "a_surname", "given": ["a_forename"]}], imms["contained"][0]["name"])

        # Surname non-empty, forename empty
        imms = copy.deepcopy(self.imms)
        _decorate_patient(imms, OrderedDict([("person_surname", "a_surname"), ("person_forename", "")]))
        self.assertListEqual([{"family": "a_surname"}], imms["contained"][0]["name"])

        # Surname empty, forename non-empty
        imms = copy.deepcopy(self.imms)
        _decorate_patient(imms, OrderedDict([("person_forename", "a_forename")]))
        self.assertListEqual([{"given": ["a_forename"]}], imms["contained"][0]["name"])

    def test_add_nhs_number(self):
        """it should add the nhs number to the patient object"""
        _decorate_patient(self.imms, OrderedDict([("nhs_number", "a_nhs_number")]))
        expected_contained_patient_identifier = [
            {"system": "https://fhir.nhs.uk/Id/nhs-number", "value": "a_nhs_number"}
        ]
        self.assertListEqual(expected_contained_patient_identifier, self.imms["contained"][0]["identifier"])

    def test_add_patient_extension(self):
        """it should add the nhs number to the patient object"""
        url = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus"
        coding_system = "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland"
        extension_base = {"extension": [{"url": url, "valueCodeableConcept": {"coding": [{"system": coding_system}]}}]}

        # nhs_number_status_indicator: _code and _description non-empty
        imms = copy.deepcopy(self.imms)
        headers = OrderedDict(
            [
                ("nhs_number_status_indicator_code", "a_status_code"),
                ("nhs_number_status_indicator_description", "a_status_description"),
            ]
        )

        _decorate_patient(imms, headers)

        expected = copy.deepcopy(extension_base)
        expected["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = "a_status_code"
        expected["extension"][0]["valueCodeableConcept"]["coding"][0]["display"] = "a_status_description"
        self.assertDictEqual(expected, imms["contained"][0]["identifier"][0])

        # nhs_number_status_indicator: _code non-empty, _description empty
        imms = copy.deepcopy(self.imms)
        headers = OrderedDict([("nhs_number_status_indicator_code", "a_status_code")])

        _decorate_patient(imms, headers)

        expected = copy.deepcopy(extension_base)
        expected["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = "a_status_code"
        self.assertDictEqual(expected, imms["contained"][0]["identifier"][0])

        # nhs_number_status_indicator: _code empty, _description non-empty
        imms = copy.deepcopy(self.imms)
        headers = OrderedDict([("nhs_number_status_indicator_description", "a_status_description")])

        _decorate_patient(imms, headers)

        expected = copy.deepcopy(extension_base)
        expected["extension"][0]["valueCodeableConcept"]["coding"][0]["display"] = "a_status_description"
        self.assertDictEqual(expected, imms["contained"][0]["identifier"][0])


class TestVaccineDecorator(unittest.TestCase):
    def setUp(self):
        self.imms = copy.deepcopy(raw_imms)

    def test_all_vaccine_headers(self):
        """Test that all vaccine fields are added when all vaccine fields contain non-empty data"""
        all_vaccine_headers = OrderedDict(
            [
                ("vaccine_product_code", "a_vacc_code"),
                ("vaccine_product_term", "a_vacc_term"),
                ("vaccine_manufacturer", "a_manufacturer"),
                ("expiry_date", "20000101"),
                ("batch_number", "a_batch_number"),
            ]
        )
        _decorate_vaccine(self.imms, all_vaccine_headers)

        expected_output = {
            "resourceType": "Immunization",
            "contained": [],
            "vaccineCode": {
                "coding": [{"system": "http://snomed.info/sct", "code": "a_vacc_code", "display": "a_vacc_term"}]
            },
            "manufacturer": {"display": "a_manufacturer"},
            "lotNumber": "a_batch_number",
            "expirationDate": "2000-01-01",
        }

        self.assertDictEqual(self.imms, expected_output)

    # TODO: Remove this one, but add to other decorators
    def test_one_header(self):
        """Test that vaccine fields are added when one vaccine field contains non-empty data"""
        _decorate_vaccine(self.imms, OrderedDict([("vaccine_product_code", "a_vacc_code")]))
        expected_output = {
            "resourceType": "Immunization",
            "contained": [],
            "vaccineCode": {"coding": [{"system": "http://snomed.info/sct", "code": "a_vacc_code"}]},
        }
        self.assertDictEqual(self.imms, expected_output)

    def test_no_headers(self):
        """Test that no fields are added when no vaccine fields contain non-empty data"""
        _decorate_vaccine(self.imms, OrderedDict([]))
        self.assertDictEqual(self.imms, {"resourceType": "Immunization", "contained": []})

    def test_vaccine_product(self):
        # vaccine_product: _code and term non-empty
        headers = OrderedDict([("vaccine_product_code", "a_vacc_code"), ("vaccine_product_term", "a_vacc_term")])
        _decorate_vaccine(self.imms, headers)
        expected = {"coding": [{"system": "http://snomed.info/sct", "code": "a_vacc_code", "display": "a_vacc_term"}]}
        self.assertDictEqual(expected, self.imms["vaccineCode"])

        # vaccine_product: _code non-empty, term empty
        headers = OrderedDict([("vaccine_product_code", "a_vacc_code"), ("vaccine_product_term", "")])
        _decorate_vaccine(self.imms, headers)
        expected = {"coding": [{"system": "http://snomed.info/sct", "code": "a_vacc_code"}]}
        self.assertDictEqual(expected, self.imms["vaccineCode"])

        # vaccine_product: _code empty, term non-empty
        headers = OrderedDict([("vaccine_product_code", ""), ("vaccine_product_term", "a_vacc_term")])
        _decorate_vaccine(self.imms, headers)
        expected = {"coding": [{"system": "http://snomed.info/sct", "display": "a_vacc_term"}]}
        self.assertDictEqual(expected, self.imms["vaccineCode"])


class TestVaccinationDecorator(unittest.TestCase):
    def setUp(self):
        self.imms = copy.deepcopy(raw_imms)

    def test_all_vaccination_headers(self):
        """Test that all vaccination fields are added when all vaccination fields contain non-empty data"""
        all_vaccination_headers = OrderedDict(
            [
                ("vaccination_procedure_code", "a_vaccination_procedure_code"),
                ("vaccination_procedure_term", "a_vaccination_procedure_term"),
                ("vaccination_situation_code", "a_vaccination_situation_code"),
                ("vaccination_situation_term", "a_vaccination_situation_term"),
                ("date_and_time", "20000101T11111101"),
                ("primary_source", "True"),
                ("report_origin", "a_report_origin"),
                ("site_of_vaccination_code", "a_vacc_site_code"),
                ("site_of_vaccination_term", "a_vacc_site_term"),
                ("route_of_vaccination_code", "a_vacc_route_code"),
                ("route_of_vaccination_term", "a_vacc_route_term"),
                ("dose_amount", "0.5"),
                ("dose_unit_term", "a_dose_unit_term"),
                ("dose_unit_code", "a_dose_unit_code"),
                ("dose_sequence", "3"),
            ]
        )
        _decorate_vaccination(self.imms, all_vaccination_headers)

        expected_output = {
            "resourceType": "Immunization",
            "contained": [],
            "extension": [vaccination_procedure_extension_item, vaccination_situation_extension_item],
            "occurrenceDateTime": "2000-01-01T11:11:11+01:00",
            "primarySource": True,
            "reportOrigin": {"text": "a_report_origin"},
            "site": {
                "coding": [
                    {"system": "http://snomed.info/sct", "code": "a_vacc_site_code", "display": "a_vacc_site_term"}
                ]
            },
            "route": {
                "coding": [
                    {"system": "http://snomed.info/sct", "code": "a_vacc_route_code", "display": "a_vacc_route_term"}
                ]
            },
            "doseQuantity": {
                "value": Decimal(0.5),
                "unit": "a_dose_unit_term",
                "system": "http://unitsofmeasure.org",
                "code": "a_dose_unit_code",
            },
            "protocolApplied": [{"doseNumberPositiveInt": 3}],
        }

        self.assertDictEqual(self.imms, expected_output)

    def test_no_headers(self):
        """Test that no fields are added when no vaccination fields contain non-empty data"""
        _decorate_vaccination(self.imms, OrderedDict([]))
        self.assertDictEqual(self.imms, {"resourceType": "Immunization", "contained": []})

    def test_one_extension_header(self):
        """Test that the relevant extension fields are added when one vaccination field contains non-empty data"""
        _decorate_vaccination(self.imms, OrderedDict([("vaccination_procedure_term", "a_vaccination_procedure_term")]))

        expected_extension_item = copy.deepcopy(vaccination_procedure_extension_item)
        expected_extension_item["valueCodeableConcept"]["coding"][0].pop("code")
        expected_output = {"resourceType": "Immunization", "contained": [], "extension": [expected_extension_item]}
        self.assertDictEqual(self.imms, expected_output)

    def test_vaccination_procedure(self):
        """it should get the vaccination procedure code and term and add it to the extension list"""
        # vaccination_procedure: _code empty, _term non-empty
        _decorate_vaccination(self.imms, OrderedDict([("vaccination_procedure_term", "a_vaccination_procedure_term")]))
        expected_extension_item = copy.deepcopy(vaccination_procedure_extension_item)
        expected_extension_item["valueCodeableConcept"]["coding"][0].pop("code")
        self.assertListEqual(self.imms["extension"], [expected_extension_item])

        # vaccination_procedure: _code empty, _term non-empty
        _decorate_vaccination(self.imms, OrderedDict([("vaccination_procedure_code", "a_vaccination_procedure_code")]))
        expected_extension_item = copy.deepcopy(vaccination_procedure_extension_item)
        expected_extension_item["valueCodeableConcept"]["coding"][0].pop("display")
        self.assertListEqual(self.imms["extension"], [expected_extension_item])

    def test_vaccination_situation(self):
        # vaccination_situation: _code empty, _term non-empty
        _decorate_vaccination(self.imms, OrderedDict([("vaccination_situation_term", "a_vaccination_situation_term")]))
        expected_extension_item = copy.deepcopy(vaccination_situation_extension_item)
        expected_extension_item["valueCodeableConcept"]["coding"][0].pop("code")
        self.assertListEqual(self.imms["extension"], [expected_extension_item])

        # vaccination_situation: _code empty, _term non-empty
        _decorate_vaccination(self.imms, OrderedDict([("vaccination_situation_code", "a_vaccination_situation_code")]))
        expected_extension_item = copy.deepcopy(vaccination_situation_extension_item)
        expected_extension_item["valueCodeableConcept"]["coding"][0].pop("display")
        self.assertListEqual(self.imms["extension"], [expected_extension_item])

    def test_site_of_vaccination(self):
        """it should get the vaccination site code and term and add it to the site object"""
        # site_of_vaccination: _code non-empty, _display empty
        _decorate_vaccination(self.imms, OrderedDict([("site_of_vaccination_code", "a_vacc_site_code")]))
        expected = {"coding": [{"system": "http://snomed.info/sct", "code": "a_vacc_site_code"}]}
        self.assertDictEqual(expected, self.imms["site"])

        # site_of_vaccination: _code empty, _display non-empty
        _decorate_vaccination(self.imms, OrderedDict([("site_of_vaccination_term", "a_vacc_site_term")]))
        expected = {"coding": [{"system": "http://snomed.info/sct", "display": "a_vacc_site_term"}]}
        self.assertDictEqual(expected, self.imms["site"])

    def test_route_of_vaccination(self):
        """it should get the vaccination route code and term and add it to the route object"""
        # route_of_vaccination: _code non-empty, _display empty
        _decorate_vaccination(self.imms, OrderedDict([("route_of_vaccination_code", "a_vacc_route_code")]))
        expected = {"coding": [{"system": "http://snomed.info/sct", "code": "a_vacc_route_code"}]}
        self.assertDictEqual(expected, self.imms["route"])

        # route_of_vaccination: _code empty, _display non-empty
        _decorate_vaccination(self.imms, OrderedDict([("route_of_vaccination_term", "a_vacc_route_term")]))
        expected = {"coding": [{"system": "http://snomed.info/sct", "display": "a_vacc_route_term"}]}
        self.assertDictEqual(expected, self.imms["route"])

    def test_dose_quantity(self):
        """it should get the dose amount, unit code and term and add it to the doseQuantity object"""
        dose_quantity = {"system": "http://unitsofmeasure.org", "value": Decimal("0.5"), "unit": "t", "code": "code"}
        # dose: _amount non-empty, _unit_term non-empty, _unit_code empty
        headers = OrderedDict([("dose_amount", "0.5"), ("dose_unit_term", "a_dose_unit_term"), ("dose_unit_code", "")])
        _decorate_vaccination(self.imms, headers)
        dose_quantity = {"system": "http://unitsofmeasure.org", "value": Decimal("0.5"), "unit": "a_dose_unit_term"}
        self.assertDictEqual(self.imms["doseQuantity"], dose_quantity)

        # dose: _amount non-empty, _unit_term empty, _unit_code non-empty
        headers = OrderedDict([("dose_amount", "0.5"), ("dose_unit_code", "a_dose_unit_code")])
        _decorate_vaccination(self.imms, headers)
        dose_quantity = {"system": "http://unitsofmeasure.org", "value": Decimal("0.5"), "code": "a_dose_unit_code"}
        self.assertDictEqual(self.imms["doseQuantity"], dose_quantity)

        # dose: _amount empty, _unit_term non-empty, _unit_code non-empty
        headers = OrderedDict([("dose_unit_term", "a_dose_unit_term"), ("dose_unit_code", "a_dose_unit_code")])
        _decorate_vaccination(self.imms, headers)
        dose_quantity = {"system": "http://unitsofmeasure.org", "code": "a_dose_unit_code", "unit": "a_dose_unit_term"}
        self.assertDictEqual(self.imms["doseQuantity"], dose_quantity)

        # dose: _amount non-empty, _unit_term empty, _unit_code empty
        headers = OrderedDict([("dose_amount", "2"), ("dose_unit_code", "")])
        _decorate_vaccination(self.imms, headers)
        dose_quantity = {"system": "http://unitsofmeasure.org", "value": 2}
        self.assertDictEqual(self.imms["doseQuantity"], dose_quantity)

        # dose: _amount empty, _unit_term non-empty, _unit_code empty
        headers = OrderedDict([("dose_unit_term", "a_dose_unit_term"), ("dose_unit_code", "")])
        _decorate_vaccination(self.imms, headers)
        dose_quantity = {"system": "http://unitsofmeasure.org", "unit": "a_dose_unit_term"}
        self.assertDictEqual(self.imms["doseQuantity"], dose_quantity)

        # dose: _amount empty, _unit_term empty, _unit_code non-empty
        headers = OrderedDict([("dose_unit_code", "a_dose_unit_code")])
        _decorate_vaccination(self.imms, headers)
        dose_quantity = {"system": "http://unitsofmeasure.org", "code": "a_dose_unit_code"}
        self.assertDictEqual(self.imms["doseQuantity"], dose_quantity)


class TestPerformerDecorator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

    def test_add_practitioner(self):
        """it should add the practitioner object to the contained list and the performer list"""
        headers = OrderedDict([("performing_professional_body_reg_code", "a_performing_professional_body_reg_code")])

        _decorate_performer(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["contained"].append({"resourceType": "Practitioner", "id": "practitioner1", "identifier": ANY})
        expected_imms["performer"] = []
        expected_imms["performer"].append({"actor": {"reference": "#practitioner1"}})

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_practitioner_identifier(self):
        headers = OrderedDict(
            [
                ("performing_professional_body_reg_code", "a_performing_professional_body_reg_code"),
                ("performing_professional_body_reg_uri", "a_performing_professional_body_reg_uri"),
            ]
        )

        _decorate_performer(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["contained"].append(
            {
                "resourceType": "Practitioner",
                "id": ANY,
                "identifier": [
                    {
                        "system": "a_performing_professional_body_reg_uri",
                        "value": "a_performing_professional_body_reg_code",
                    }
                ],
            }
        )
        expected_imms["performer"] = []
        expected_imms["performer"].append(ANY)

        self.assertDictEqual(expected_imms, self.imms)

    def test_practitioner_name(self):
        """it should add practitioner name"""
        headers = OrderedDict(
            [
                ("performing_professional_body_reg_code", "a_performing_professional_body_reg_code"),
                ("performing_professional_forename", "a_performing_professional_forename"),
                ("performing_professional_surname", "a_performing_professional_surname"),
            ]
        )

        _decorate_performer(self.imms, headers)

        expected_imms = copy.deepcopy(raw_imms)
        expected_imms["contained"].append(
            {
                "resourceType": "Practitioner",
                "id": ANY,
                "identifier": ANY,
                "name": [
                    {"family": "a_performing_professional_surname", "given": ["a_performing_professional_forename"]}
                ],
            }
        )
        expected_imms["performer"] = []
        expected_imms["performer"].append(ANY)

        self.assertDictEqual(expected_imms, self.imms)

    def test_add_organisation(self):
        """it should add the organisation where the vaccination was given based on the site code"""
        headers = OrderedDict(
            [
                ("site_code", "a_site_code"),
                ("site_code_type_uri", "a_site_code_type_uri"),
                ("site_name", "a_site_name"),
            ]
        )

        _decorate_performer(self.imms, headers)

        expected = {
            "actor": {
                "type": "Organization",
                "identifier": {"system": "a_site_code_type_uri", "value": "a_site_code"},
                "display": "a_site_name",
            }
        }

        self.assertDictEqual(expected, self.imms["performer"][0])

    def test_location(self):
        """it should get the location code and type and add it to the location object"""
        headers = OrderedDict(
            [
                ("location_code", "a_location_code"),
                ("location_code_type_uri", "a_location_code_type_uri"),
            ]
        )

        _decorate_performer(self.imms, headers)

        expected = {
            "type": "Location",
            "identifier": {"value": "a_location_code", "system": "a_location_code_type_uri"},
        }

        self.assertDictEqual(expected, self.imms["location"])


class TestQuestionnaireDecorator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.imms = copy.deepcopy(raw_imms)

    @staticmethod
    def _make_questionare(imms: dict, name: str, item: dict):
        questionare = {
            "resourceType": "QuestionnaireResponse",
            "id": ANY,
            "status": ANY,
            "item": [{"linkId": name, "answer": [item]}],
        }
        imms["contained"].append(questionare)

    @staticmethod
    def _make_questionare_item(name: str, item: dict):
        return {"linkId": name, "answer": [item]}

    @staticmethod
    def _add_questionare_item(imms: dict, name: str, item: dict):
        imms["contained"][0]["item"].append({"linkId": name, "answer": [item]})

    def test_reduce_validation_code(self):
        """it should add the reduceValidation if provided with the default value of false"""
        headers = OrderedDict([("reduce_validation_code", "True")])

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item("ReduceValidation", {"valueBoolean": True})

        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_reduce_validation_reason(self):
        """it should add the ReduceValidationReason if code is provided"""
        headers = OrderedDict(
            [
                ("reduce_validation_code", "True"),
                ("reduce_validation_reason", "a_reduce_validation_reason"),
            ]
        )

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item(
            "ReduceValidationReason", {"valueString": "a_reduce_validation_reason"}
        )

        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_consent(self):
        """it should add the consent to the questionare list"""
        headers = OrderedDict(
            [
                ("consent_for_treatment_code", "a_consent_for_treatment_code"),
                ("consent_for_treatment_description", "a_consent_for_treatment_description"),
            ]
        )

        _decorate_questionare(self.imms, headers)

        item = {
            "valueCoding": {
                "code": "a_consent_for_treatment_code",
                "display": "a_consent_for_treatment_description",
            }
        }
        expected_item = self._make_questionare_item("Consent", item)

        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_care_setting(self):
        """it should add the care setting to the questionare list"""
        headers = OrderedDict(
            [
                ("care_setting_type_code", "a_care_setting_type_code"),
                ("care_setting_type_description", "a_care_setting_type_description"),
            ]
        )

        _decorate_questionare(self.imms, headers)

        item = {
            "valueCoding": {
                "code": "a_care_setting_type_code",
                "display": "a_care_setting_type_description",
            }
        }
        expected_item = self._make_questionare_item("CareSetting", item)

        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_local_patient(self):
        """it should add the local patient to the questionare list"""
        headers = OrderedDict(
            [
                ("local_patient_id", "a_local_patient_id"),
                ("local_patient_uri", "a_local_patient_uri"),
            ]
        )

        _decorate_questionare(self.imms, headers)

        item = {"valueReference": {"identifier": {"system": "a_local_patient_uri", "value": "a_local_patient_id"}}}
        expected_item = self._make_questionare_item("LocalPatient", item)
        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_ip_address(self):
        """it should add the ip address to the questionare list"""
        headers = OrderedDict([("ip_address", "a_ip_address")])

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item("IpAddress", {"valueString": "a_ip_address"})
        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_user_id(self):
        """it should add the user id to the questionare list"""
        headers = OrderedDict([("user_id", "a_user_id")])

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item("UserId", {"valueString": "a_user_id"})
        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_user_name(self):
        """it should add the user name to the questionare list"""
        headers = OrderedDict([("user_name", "a_user_name")])

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item("UserName", {"valueString": "a_user_name"})
        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_user_email(self):
        """it should add the user email to the questionare list"""
        headers = OrderedDict([("user_email", "a_user_email")])

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item("UserEmail", {"valueString": "a_user_email"})
        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_submitted_timestamp(self):
        """it should convert and add the submitted timestamp to the questionare list"""
        headers = OrderedDict([("submitted_timestamp", "20240221T17193000")])

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item(
            "SubmittedTimeStamp", {"valueDateTime": "2024-02-21T17:19:30+00:00"}
        )
        self.assertIn(expected_item, self.imms["contained"][0]["item"])

    def test_add_performer_job_role(self):
        """it should add the performer job role to the questionare list"""
        headers = OrderedDict([("sds_job_role_name", "a_sds_job_role_name")])

        _decorate_questionare(self.imms, headers)

        expected_item = self._make_questionare_item("PerformerSDSJobRole", {"valueString": "a_sds_job_role_name"})
        self.assertIn(expected_item, self.imms["contained"][0]["item"])
