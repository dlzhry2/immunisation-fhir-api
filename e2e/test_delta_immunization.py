from datetime import datetime
from utils.base_test import ImmunizationBaseTest
from utils.resource import create_an_imms_obj


class TestDeltaImmunization(ImmunizationBaseTest):
    def test_create_delta_imms(self):
        """it should create a FHIR Immunization resource"""
        for imms_api in self.imms_apis:
            with self.subTest(imms_api):
                # Given
                imms = create_an_imms_obj()
                start_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                # When
                response = imms_api.create_immunization(imms)
                end_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                print("TABLLEEE", self.imms_delta_table)
                # Then
                if response.status_code == 201:
                    print("SUCCESS FROM CREATE  ")
                    operation = "CREATE"
                    results = []

                    expression_attribute_values = {
                        ":start": start_timestamp,
                        ":end": end_timestamp,
                        ":operation": operation,
                    }

                    key_condition_expression = "Operation = :operation AND DateTimeStamp BETWEEN :start AND :end"
                    response = self.imms_delta_table.query(
                        IndexName="SearchIndex",
                        KeyConditionExpression=key_condition_expression,
                        ExpressionAttributeValues=expression_attribute_values,
                    )
                    print("RESPONSEEEE ", response)
                    results.extend(response["Items"])

                    self.assertEqual(response.status_code, 201, response.text)
                    self.assertEqual(response.text, "")
                    self.assertTrue("Location" in response.headers)
