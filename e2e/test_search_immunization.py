import logging
import uuid

from utils.base_test import ImmunizationBaseTest
from utils.constants import valid_nhs_number1, valid_nhs_number2
from utils.resource import create_an_imms_obj

flu_code = "mockFLUcode1"
mmr_code = "mockMMRcode1"
covid_code = "1324681000000101"


class TestSearchImmunization(ImmunizationBaseTest):
    # fill this field and it'll get deleted after each test method
    stored_imms: list

    def tearDown(self):
        for res in self.stored_imms:
            response = self.app_res_imms_api.delete_immunization(res["id"])
            if response.status_code != 204:
                logging.warning(f"failed to cleanup resource: {res['id']}\n{response.text}")

    def store_records(self, *resources):
        for res in resources:
            imms_id = self.create_immunization_resource(self.app_res_imms_api, res)
            res["id"] = imms_id
        # store it in the class field so, we can clean it up after test
        self.stored_imms = list(resources)

    def test_search_imms(self):
        """it should search records given nhs-number and disease-code"""
        for imms_api in self.imms_apis:
            with self.subTest(imms_api):
                # Given two patients each with one mmr
                mmr_p1 = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, mmr_code)
                mmr_p2 = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number2, flu_code)
                self.store_records(mmr_p1, mmr_p2)

                # When
                response = self.app_res_imms_api.search_immunizations(valid_nhs_number1, "MMR")
                # Then
                self.assertEqual(response.status_code, 200, response.text)
                body = response.json()
                self.assertEqual(body["resourceType"], "Bundle")

                resource_ids = [entity["resource"]["id"] for entity in body["entry"]]
                self.assertEqual(len(resource_ids), 1)
                self.assertEqual(resource_ids[0], mmr_p1["id"])

    def test_search_patient_multiple_diseases(self):
        # Given patient has two vaccines
        mmr = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, mmr_code)
        flu = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, flu_code)
        self.store_records(mmr, flu)

        # When
        response = self.app_res_imms_api.search_immunizations(valid_nhs_number1, "MMR")

        # Then
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()

        # make sure the match is the one we are expecting
        resource_ids = [entity["resource"]["id"] for entity in body["entry"]]
        self.assertEqual(len(resource_ids), 1)
        self.assertEqual(resource_ids[0], mmr["id"])

    def test_search_ignore_deleted(self):
        # Given patient has three vaccines and the last one is deleted
        mmr1 = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, mmr_code)
        mmr2 = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, mmr_code)
        self.store_records(mmr1, mmr2)

        to_delete_mmr = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, mmr_code)
        deleted_mmr = self.create_a_deleted_immunization_resource(self.app_res_imms_api, to_delete_mmr)

        # When
        response = self.app_res_imms_api.search_immunizations(valid_nhs_number1, "MMR")

        # Then
        self.assertEqual(response.status_code, 200, response.text)

        body = response.json()
        resource_ids = [entity["resource"]["id"] for entity in body["entry"]]
        self.assertEqual(len(resource_ids), 2)
        self.assertTrue(deleted_mmr["id"] not in resource_ids)
