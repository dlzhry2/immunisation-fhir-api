import unittest
from moto import mock_s3, mock_sqs
import boto3
import os
import json
from boto3 import client as boto3_client
from ack_processor import lambda_handler
from tests.utils_ack_processor import (
SOURCE_BUCKET_NAME,
DESTINATION_BUCKET_NAME,
AWS_REGION
)
s3_client = boto3_client("s3", region_name=AWS_REGION)

@mock_s3
@mock_sqs
class TestAckProcessorE2E(unittest.TestCase):

    def setup_s3(self):
        """Helper to setup mock S3 buckets and upload test file"""
        s3_client.create_bucket(
            Bucket=DESTINATION_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
        )

    
    def test_ack_processor_Invalid_action_flag(self):
        # Add a message to the SQS queue
        # Simulate event for Lambda
        self.setup_s3()
        event = {'Records': [{'messageId': '33823a19-8cbd-427b-8141-308d899bce42', 'receiptHandle': 'AQEBovTE47h7VtU+vzCiWD5hKQez1RAw8guw6lGgwn8KgFGPkopsdzk7+ozeIbA6MjHfndseBFDFP2qSzqESCWXrpQuRPHuk934W90vh/a8A7WIfP2BG/3AqPjbuJUr7IjboHmXQohV9/Vhg2tx5PBi6XhbwL99PmHqhf4lpX7/ryHbPKIvVz/eQ0eim7etHJzpDpF8vpqU2Rm25RZyWjIS6TddFc2H+LkDE/0wQ03LMJeHm5IyFpmD7qBztNfPj38crQXz9+W69lE1T+l82mdhpunia2g6Kygaxh1n+DLNnxeKxJVBdGgOQNw1+IFsQrmUD', 'body': '{"row_id": "855d9cf2-31ef-44ef-8479-8785cf908759#1", "file_key": "COVID19_Vaccinations_v5_YGM41_20240909T13005901.csv", "supplier": "EMIS", "created_at_formatted_string": "20241115T13435500", "diagnostics": "Invalid ACTION_FLAG - ACTION_FLAG must be \'NEW\', \'UPDATE\' or \'DELETE\'", "operation_requested": ""}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1731678275968', 'SequenceNumber': '18890053712357359616', 'MessageGroupId': 'COVID19_Vaccinations_v5_YGM41_20240909T13005901.csv', 'SenderId': 'AROAVA5YK2MEKOYMJQMAN:a45be4bff5d545eba5d150bf48ce4f83', 'MessageDeduplicationId': '17029e8e38ab35a9e2467bf4ef8727473753f82df3fe361c0fe8bfc00c396538', 'ApproximateFirstReceiveTimestamp': '1731678275968'}, 'messageAttributes': {}, 'md5OfBody': 'dd31619757448cf55522c64d2c618304', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-2:345594581768:imms-internal-dev-ack-metadata-queue.fifo', 'awsRegion': 'eu-west-2'}]}

        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_key = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240909T13005901_BusAck.csv"
        ack_file_content = s3_client.get_object(Bucket=DESTINATION_BUCKET_NAME, Key=ack_file_key)["Body"].read().decode("utf-8")

        # Assert acknowledgment file content
        self.assertIn("Fatal Error", ack_file_content)  
        self.assertIn("Invalid ACTION_FLAG - ACTION_FLAG must be 'NEW', 'UPDATE' or 'DELETE'", ack_file_content)
        

    def test_ack_processor_imms_not_found(self):
        # Add a message to the SQS queue
        # Simulate event for Lambda
        self.setup_s3()
        event = {'Records': [{'messageId': '33823a19-8cbd-427b-8141-308d899bce42', 'receiptHandle': 'AQEBovTE47h7VtU+vzCiWD5hKQez1RAw8guw6lGgwn8KgFGPkopsdzk7+ozeIbA6MjHfndseBFDFP2qSzqESCWXrpQuRPHuk934W90vh/a8A7WIfP2BG/3AqPjbuJUr7IjboHmXQohV9/Vhg2tx5PBi6XhbwL99PmHqhf4lpX7/ryHbPKIvVz/eQ0eim7etHJzpDpF8vpqU2Rm25RZyWjIS6TddFc2H+LkDE/0wQ03LMJeHm5IyFpmD7qBztNfPj38crQXz9+W69lE1T+l82mdhpunia2g6Kygaxh1n+DLNnxeKxJVBdGgOQNw1+IFsQrmUD', 'body': '{"row_id": "855d9cf2-31ef-44ef-8479-8785cf908759#1", "file_key": "COVID19_Vaccinations_v5_YGM41_20240909T13005901.csv", "supplier": "EMIS", "created_at_formatted_string": "20241115T13435500", "diagnostics": "Imms id not found", "operation_requested": ""}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1731678275968', 'SequenceNumber': '18890053712357359616', 'MessageGroupId': 'COVID19_Vaccinations_v5_YGM41_20240909T13005901.csv', 'SenderId': 'AROAVA5YK2MEKOYMJQMAN:a45be4bff5d545eba5d150bf48ce4f83', 'MessageDeduplicationId': '17029e8e38ab35a9e2467bf4ef8727473753f82df3fe361c0fe8bfc00c396538', 'ApproximateFirstReceiveTimestamp': '1731678275968'}, 'messageAttributes': {}, 'md5OfBody': 'dd31619757448cf55522c64d2c618304', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-2:345594581768:imms-internal-dev-ack-metadata-queue.fifo', 'awsRegion': 'eu-west-2'}]}

        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_key = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240909T13005901_BusAck.csv"
        ack_file_content = s3_client.get_object(Bucket=DESTINATION_BUCKET_NAME, Key=ack_file_key)["Body"].read().decode("utf-8")

        # Assert acknowledgment file content
        self.assertIn("Fatal Error", ack_file_content)  
        self.assertIn("Imms id not found", ack_file_content)

    def test_ack_processor_unique_id_or_uri_missing(self):
        # Add a message to the SQS queue
        # Simulate event for Lambda
        self.setup_s3()
        event = {'Records': [{'messageId': '33823a19-8cbd-427b-8141-308d899bce42', 'receiptHandle': 'AQEBovTE47h7VtU+vzCiWD5hKQez1RAw8guw6lGgwn8KgFGPkopsdzk7+ozeIbA6MjHfndseBFDFP2qSzqESCWXrpQuRPHuk934W90vh/a8A7WIfP2BG/3AqPjbuJUr7IjboHmXQohV9/Vhg2tx5PBi6XhbwL99PmHqhf4lpX7/ryHbPKIvVz/eQ0eim7etHJzpDpF8vpqU2Rm25RZyWjIS6TddFc2H+LkDE/0wQ03LMJeHm5IyFpmD7qBztNfPj38crQXz9+W69lE1T+l82mdhpunia2g6Kygaxh1n+DLNnxeKxJVBdGgOQNw1+IFsQrmUD', 'body': '{"row_id": "855d9cf2-31ef-44ef-8479-8785cf908759#1", "file_key": "COVID19_Vaccinations_v5_YGM41_20240909T13005901.csv", "supplier": "EMIS", "created_at_formatted_string": "20241115T13435500", "diagnostics": "UNIQUE_ID or UNIQUE_ID_URI is missing", "operation_requested": ""}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1731678275968', 'SequenceNumber': '18890053712357359616', 'MessageGroupId': 'COVID19_Vaccinations_v5_YGM41_20240909T13005901.csv', 'SenderId': 'AROAVA5YK2MEKOYMJQMAN:a45be4bff5d545eba5d150bf48ce4f83', 'MessageDeduplicationId': '17029e8e38ab35a9e2467bf4ef8727473753f82df3fe361c0fe8bfc00c396538', 'ApproximateFirstReceiveTimestamp': '1731678275968'}, 'messageAttributes': {}, 'md5OfBody': 'dd31619757448cf55522c64d2c618304', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-2:345594581768:imms-internal-dev-ack-metadata-queue.fifo', 'awsRegion': 'eu-west-2'}]}

        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_key = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240909T13005901_BusAck.csv"
        ack_file_content = s3_client.get_object(Bucket=DESTINATION_BUCKET_NAME, Key=ack_file_key)["Body"].read().decode("utf-8")

        # Assert acknowledgment file content
        self.assertIn("Fatal Error", ack_file_content)  
        self.assertIn("UNIQUE_ID or UNIQUE_ID_URI is missing", ack_file_content)

    
    def test_ack_processor_create_success(self):
        # Add a message to the SQS queue
        # Simulate event for Lambda
        self.setup_s3()
        event = {'Records': [{'messageId': '34138062-a94a-4cfc-aade-1b76019bba7e', 'receiptHandle': 'AQEBbO6pKl7lgVbWy+ZQ79KIrjj8Weg94HrgL1otGRP5z7NgRdT1dm1nu8OEBCi/4/BvqWqdwFCi3JUWqDItKfjCGNMnXtbUT7yYYd5LMgmDmbeiVjm7rpWVYq+G0NTEI9y6GOB+5OScU3+W9UNLVDujoyjxJSYcGH+LBMUM6C8g/OTO03EWLFDdGVZJR2RYlsjavnN4xlNd98XDTRMX1eiyWglzbWdfVt9vmreSGNlj179vozWgWyp/cEoetAUXpMZtNIgqS1W41BQUG44SHcIcEZQ6CJsL0rtFGPQM0UKCadzVposkJbhnysn54o6dvUW4', 'body': '{"statusCode": 201, "headers": {"Location": "https://internal-dev.api.service.nhs.uk/immunisation-fhir-api/Immunization/719aef39-64b1-4e7b-981e-4acb64e8538e"}, "file_key": "COVID19_Vaccinations_v5_YGM41_20240927T13005901.csv", "row_id": "6cd75847-e378-451f-984e-b55fa5444b50#1", "created_at_formatted_string": "20241119T11182100"}', 'attributes': {'ApproximateReceiveCount': '1', 'AWSTraceHeader': 'Root=1-673c7427-2b2628f92f49a74958f7a4ad;Parent=55ff249c7851b249;Sampled=0;Lineage=2:7569cfea:0', 'SentTimestamp': '1732015146225', 'SequenceNumber': '18890139951143151616', 'MessageGroupId': 'COVID19_Vaccinations_v5_YGM41_20240927T13005901.csv', 'SenderId': 'AROAVA5YK2MEPKLV7YKKW:imms-internal-dev_create_imms', 'MessageDeduplicationId': 'bd586317714866a7300128236b2e4eeac088b1d80d886282989b6dfa9094a834', 'ApproximateFirstReceiveTimestamp': '1732015146225'}, 'messageAttributes': {}, 'md5OfBody': 'c95b2280b88a00e1b647a3619ec529ce', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-2:345594581768:imms-internal-dev-ack-metadata-queue.fifo', 'awsRegion': 'eu-west-2'}]}

        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_key = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240927T13005901_BusAck.csv"
        ack_file_content = s3_client.get_object(Bucket=DESTINATION_BUCKET_NAME, Key=ack_file_key)["Body"].read().decode("utf-8")

        # Assert acknowledgment file content
        self.assertIn("OK", ack_file_content)  
        self.assertIn("719aef39-64b1-4e7b-981e-4acb64e8538e", ack_file_content) 

    def test_ack_processor_create_duplicate(self):
        # Add a message to the SQS queue
        # Simulate event for Lambda
        self.setup_s3()
        event = {'Records': [{'messageId': '9905ffd7-e155-42cb-90bf-77fa69cd3bce', 'receiptHandle': 'AQEBLkCkOqdC7dCFkh7XmM9nAfdB57Jgide7oouxoGe/NViTGLNAHYh7LnngfeSwDjwcGhaoWSUmvbAGZ0pIEzNrvU7Q6x+diG59bgBnlHs40AurIhLw2w5O9GKS12alRQMAO2Dkb1xkUL1TK1yiejV4nSeRPuNhcbCwltoJhZ8uD5Z93s4ZRgC7qsGrkG7lmy26OYMdGS9Dmf/KoEXWgAIhmu1Fb1wmFxo/xBgsODjAgLzV9oI7YRDidT8UnNoqQCoDAVtp6NJEtuCs2yHRaBaZu2+LAVcg61dvN6Lm1tlt1d7tlaQ1Oy13u1UuKtfX66WJ', 'body': '{"statusCode": 422, "headers": {"Content-Type": "application/fhir+json"}, "body": "{\\"resourceType\\": \\"OperationOutcome\\", \\"id\\": \\"e51e9e59-4d57-41bc-b21f-5ef95547eaac\\", \\"meta\\": {\\"profile\\": [\\"https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome\\"]}, \\"issue\\": [{\\"severity\\": \\"error\\", \\"code\\": \\"duplicate\\", \\"details\\": {\\"coding\\": [{\\"system\\": \\"https://fhir.nhs.uk/Codesystem/http-error-codes\\", \\"code\\": \\"DUPLICATE\\"}]}, \\"diagnostics\\": \\"The provided identifier: https://www.ravs.england.nhs.uk/#0001_RSV_v5_Run3_valid_dose_1_new_upd_del_20240905130057 is duplicated\\"}]}", "file_key": "COVID19_Vaccinations_v5_YGM41_20240927T13005901.csv", "row_id": "8fb764cf-93af-453f-9246-ea6cd6244069#1", "created_at_formatted_string": "20241119T11554300"}', 'attributes': {'ApproximateReceiveCount': '1', 'AWSTraceHeader': 'Root=1-673c7ce9-a0c5536484aabac4abbe6714;Parent=0d306f1ed67decd1;Sampled=0;Lineage=2:7569cfea:0', 'SentTimestamp': '1732017388293', 'SequenceNumber': '18890140525112559872', 'MessageGroupId': 'COVID19_Vaccinations_v5_YGM41_20240927T13005901.csv', 'SenderId': 'AROAVA5YK2MEPKLV7YKKW:imms-internal-dev_create_imms', 'MessageDeduplicationId': 'bdda72752148d25d7a44f2c660baa4f05911818d240319ed5ec4412de18bedd9', 'ApproximateFirstReceiveTimestamp': '1732017388293'}, 'messageAttributes': {}, 'md5OfBody': '9109c54d923716c6948ec29b17baf558', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-2:345594581768:imms-internal-dev-ack-metadata-queue.fifo', 'awsRegion': 'eu-west-2'}]}

        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_key = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240927T13005901_BusAck.csv"
        ack_file_content = s3_client.get_object(Bucket=DESTINATION_BUCKET_NAME, Key=ack_file_key)["Body"].read().decode("utf-8")

        # Assert acknowledgment file content
        self.assertIn("Fatal Error", ack_file_content)  
        self.assertIn("The provided identifier: https://www.ravs.england.nhs.uk/#0001_RSV_v5_Run3_valid_dose_1_new_upd_del_20240905130057 is duplicated", ack_file_content)     

    def test_ack_processor_update_and_delete_success(self):
        # Add a message to the SQS queue
        # Simulate event for Lambda
        self.setup_s3()
        event = {'Records': [{'messageId': '1bbbfb7f-6978-4df9-806e-6f77298f4e7a', 'receiptHandle': 'AQEBSq0pPf5jlDzLi3Dn14cFKgLNgdEomNQVfzin7CrLTrNHS2z5T3Lw0GHDjhEaGw29vbBf1Glo+xCDHBEsi1tYD7ew3Lt13CreZcloSIw82jH3BRaFaXleYwsamlf7p57OLNs+xtT4n7mmv5yAJhZPaM3Hp4+91O7YSYmVXrnSH2fnMk4KoGnH3zGYFj7wBUYozRpdUTQKDKLN7n659cT6arjHPqbj4xIKtVU2QHnFAzRUcAlBTxHaaFfmpxdbtc6nab208Ndq5IXpuMoxkWsK7VCbqK+Zau34PVCUkVYlpnZDQrk9Ml2wMXXReckUYDjR', 'body': '{"statusCode": 200, "headers": {}, "file_key": "COVID19_Vaccinations_v5_YGM41_20240928T13005901.csv", "row_id": "565d8c47-25ee-4958-a59b-3a4fc0e8c6da#1", "created_at_formatted_string": "20241119T11344900"}', 'attributes': {'ApproximateReceiveCount': '1', 'AWSTraceHeader': 'Root=1-673c7804-6413a914e128d8af1c40ff2d;Parent=113952824a97cae9;Sampled=0;Lineage=2:c1d42c4f:0', 'SentTimestamp': '1732016136904', 'SequenceNumber': '18890140204756975872', 'MessageGroupId': 'COVID19_Vaccinations_v5_YGM41_20240928T13005901.csv', 'SenderId': 'AROAVA5YK2MEFVDWBRNMS:imms-internal-dev_update_imms', 'MessageDeduplicationId': 'bd590120c3dd59b92faa94e015ba0fd084c60f597896f8f32a00fa278b689585', 'ApproximateFirstReceiveTimestamp': '1732016136904'}, 'messageAttributes': {}, 'md5OfBody': 'fc4189827d499d1b41fb2154917a9579', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-2:345594581768:imms-internal-dev-ack-metadata-queue.fifo', 'awsRegion': 'eu-west-2'}]}

        # Invoke the Lambda function
        response = lambda_handler(event, context={})

        # Assert Lambda execution success
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Lambda function executed successfully", response["body"])

        # Verify the acknowledgment file in the ack bucket
        ack_file_key = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240928T13005901_BusAck.csv"
        ack_file_content = s3_client.get_object(Bucket=DESTINATION_BUCKET_NAME, Key=ack_file_key)["Body"].read().decode("utf-8")

        # Assert acknowledgment file content
        self.assertIn("OK", ack_file_content)  
     
    def tearDown(self):
        # Clean up mock resources
        os.environ.pop("ACK_BUCKET_NAME", None)


if __name__ == "__main__":
    unittest.main()
