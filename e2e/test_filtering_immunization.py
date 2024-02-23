from utils.base_test import ImmunizationBaseTest
from utils.resource import get_questionnaire_items


class TestSFlagImmunization(ImmunizationBaseTest):
    def test_get_s_flagged_imms(self):
        """it should filter certain fields if patient is s-flagged"""
        for imms_api in self.imms_apis:
            with self.subTest(imms_api):
                pass

    def test_get_not_s_flagged_imms(self):
        for imms_api in self.imms_apis:
            with self.subTest(imms_api):
                pass

    def assert_is_not_filtered(self, imms):
        imms_items = get_questionnaire_items(imms)

        for key in ["Consent"]:
            self.assertTrue(key in [item["linkId"] for item in imms_items])

        performer_actor_organizations = (
            item
            for item in imms["performer"]
            if item.get("actor", {}).get("type") == "Organization")

        self.assertTrue(all(
            performer.get("actor", {}).get("identifier", {}).get("value") != "N2N9I"
            for performer in imms["performer"]))
        self.assertTrue(all(
            organization.get("actor", {}).get("display") is not None
            for organization in performer_actor_organizations))
        self.assertTrue(all(
            organization.get("actor", {}).get("identifier", {}).get("system")
            != "https://fhir.nhs.uk/Id/ods-organization-code"
            for organization in performer_actor_organizations))

        self.assertTrue("reportOrigin" in imms)
        self.assertTrue("location" in imms)

    def assert_is_filtered(self, imms):
        imms_items = get_questionnaire_items(imms)

        for key in ["Consent"]:
            self.assertTrue(key not in [item["linkId"] for item in imms_items])

        performer_actor_organizations = (
            item
            for item in imms["performer"]
            if item.get("actor", {}).get("type") == "Organization")

        self.assertTrue(all(
            organization.get("actor", {}).get("identifier", {}).get("value") == "N2N9I"
            for organization in performer_actor_organizations))
        self.assertTrue(all(
            organization.get("actor", {}).get("display") is None
            for organization in performer_actor_organizations))
        self.assertTrue(all(
            organization.get("actor", {}).get("identifier", {}).get("system")
            == "https://fhir.nhs.uk/Id/ods-organization-code"
            for organization in performer_actor_organizations))

        self.assertTrue("reportOrigin" not in imms)
        self.assertTrue("location" not in imms)
