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
                result = imms_api.create_immunization(imms)

                # Then
                self.assertEqual(result.status_code, 201, result.text)
                self.assertEqual(result.text, "")
                self.assertTrue("Location" in result.headers)

    def test_bad_nhs_number(self):
        """it should reject the request if nhs-number does not exist"""
        bad_nhs_number = "7463384756"
        imms = create_an_imms_obj(nhs_number=bad_nhs_number)

        result = self.app_res_imms_api.create_immunization(imms)

        self.assert_operation_outcome(result, 400, bad_nhs_number)

    def test_validation(self):
        """it should validate Immunization"""
        # NOTE: This e2e test is here to prove validation logic is wired to the backend.
        #  validation is thoroughly unit tested in the backend code
        imms = create_an_imms_obj()
        invalid_datetime = "2020-12-14"
        imms["occurrenceDateTime"] = invalid_datetime

        # When
        response = self.app_res_imms_api.create_immunization(imms)

        # Then
        self.assert_operation_outcome(response, 400, "occurrenceDateTime")
