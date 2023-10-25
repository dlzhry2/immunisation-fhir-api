import json
import os
import uuid
from time import time

from boto3 import resource

from services import ImmunisationApi, S3Service


def batch_processing_handler3(event, context, api):
    if (
        "Records" in event
        and isinstance(event["Records"], list)
        and len(event["Records"]) > 0
    ):
        response_list = []

        for obj in event["Records"]:
            s3_record = obj["s3"]
            if "bucket" in s3_record and isinstance(s3_record["bucket"], dict):
                print(s3_record["bucket"])
                source_bucket_name = s3_record["bucket"].get("name")

                if "object" in s3_record and isinstance(s3_record["object"], dict):
                    print(s3_record["object"])
                    dest_bucket_name = source_bucket_name.replace(
                        "source", "destination"
                    )
                    output_bucket = resource("s3").Bucket(dest_bucket_name)
                    api_gateway_url = os.getenv("SERVICE_DOMAIN_NAME")
                    object_path = s3_record["object"]

                    try:
                        headers = {
                            "Content-Type": "application/json",
                            "User-Agent": "batch-processing-lambda",
                        }

                        request_body = json.dumps(object_path)
                        filename = f"output_report_{time()}.txt"
                        request_id = str(uuid.uuid4())

                        payload_for_output_bucket = {
                            "timestamp": filename,
                            "level": request_body,
                            "request": {
                                "x-request-id": request_id,
                                "x-correlation-id": request_id,
                            },
                        }

                        payload_for_api_gateway = {
                            "id": request_id,
                            "message": request_body,
                        }

                        payload_bytes_output_bucket = json.dumps(
                            payload_for_output_bucket
                        ).encode("utf-8")
                        payload_bytes_api_gateway = json.dumps(
                            payload_for_api_gateway
                        ).encode("utf-8")

                        # connection = http.client.HTTPSConnection(api_gateway_url)
                        # connection.request(
                        #    "POST", "/", payload_bytes_api_gateway, headers=headers
                        # )

                        response = api.post_event(payload_bytes_api_gateway, headers)

                        # response = connection.getresponse()
                        # print(response.status)
                        json_data = json.loads(response.read().decode("utf-8"))
                        # connection.close()

                        response_object = {
                            "statusCode": response.status,
                            "json": json_data,
                            "file": filename,
                        }

                        if response.status in [200, 201]:
                            response_object.update(
                                {
                                    "body": "Successfully sent JSON data to the API Gateway."
                                }
                            )
                        else:
                            response_object.update({"body": response.reason})
                            output_bucket.put_object(
                                Body=payload_bytes_output_bucket, Key="body"
                            )

                        response_list.append(response_object)

                    except Exception as e:
                        output_bucket.put_object(
                            Body=payload_bytes_output_bucket, Key="body"
                        )
                        response_list.append(
                            {
                                "statusCode": 500,
                                "body": "internal server error",
                                "message": str(e),
                            }
                        )
        return response_list
    else:
        return {"statusCode": 400, "body": "Invalid event structure."}


def batch_processing_handler(event, context):
    imms_api_url = os.getenv("SERVICE_DOMAIN_NAME")
    imms_api = ImmunisationApi(imms_api_url)
    s3_service = S3Service("source", "destination")

    status = batch_processing(event, context, s3_service, imms_api)
    return status


def batch_processing(event, context, s3_service, imms_api):
    records = event["Records"]
    for record in records:
        key = record["s3"]["object"]["key"]
        csv = s3_service.get_s3_object(key)
        errors = []
        for csv_record in csv:
            response = imms_api.post_event(csv_record)
            if response["statusCode"] == 400:
                errors.append("error")

        s3_service.write_error_report(errors)

    return "dfd"
