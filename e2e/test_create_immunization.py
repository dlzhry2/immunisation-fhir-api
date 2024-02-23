from utils.base_test import ImmunizationBaseTest
from utils.resource import create_an_imms_obj


class TestCreateImmunization(ImmunizationBaseTest):

    def test_create_imms(self):
        """it should create a FHIR Immunization resource"""
        for imms_api in self.imms_apis:
            with self.subTest(imms_api):
                # Given
                imms = create_an_imms_obj()

                # When
                result = self.app_res_imms_api.create_immunization(imms)

                # Then
                self.assertEqual(result.status_code, 201 , result.text)
                self.assertEqual(result.text, "")
                self.assertTrue("Location" in result.headers)

    def test_bad_nhs_number(self):
        """it should reject the request if nhs-number does not exist"""
        bad_nhs_number = "7463384756"
        imms = create_an_imms_obj(nhs_number=bad_nhs_number)

        result = self.app_res_imms_api.create_immunization(imms)

        self.assert_operation_outcome(result, 400, bad_nhs_number)

