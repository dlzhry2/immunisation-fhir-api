
import os
import boto3
import time
import csv
import pandas as pd
import pytz
import uuid
from datetime import datetime
import csv
from clients import logger, s3_client
from constants import ACK_BUCKET, ACK_PREFIX

def generate_csv(fore_name, dose_amount):
    """
    Generate a CSV file with 3 rows and unique GUIDs for UNIQUE_ID.
    Filename is timestamped for uniqueness.
    """
    unique_ids = [str(uuid.uuid4()) for _ in range(3)]
    data = []
    for i in range(3):
        row = {
            "NHS_NUMBER": "9732928395",
            "PERSON_FORENAME": fore_name,
            "PERSON_SURNAME": "James",
            "PERSON_DOB": "20080217",
            "PERSON_GENDER_CODE": "0",
            "PERSON_POSTCODE": "WD25 0DZ",
            "DATE_AND_TIME": datetime.utcnow().strftime("%Y%m%dT%H%M%S"),
            "SITE_CODE": "RVVKC",
            "SITE_CODE_TYPE_URI": "https://fhir.nhs.uk/Id/ods-organization-code",
            "UNIQUE_ID": unique_ids[i],
            "UNIQUE_ID_URI": "https://www.ravs.england.nhs.uk/",
            "ACTION_FLAG": "new",
            "PERFORMING_PROFESSIONAL_FORENAME": "PHYLIS",
            "PERFORMING_PROFESSIONAL_SURNAME": "James",
            "RECORDED_DATE": datetime.utcnow().strftime("%Y%m%d"),
            "PRIMARY_SOURCE": "TRUE",
            "VACCINATION_PROCEDURE_CODE": "956951000000104",
            "VACCINATION_PROCEDURE_TERM": "RSV vaccination in pregnancy (procedure)",
            "DOSE_SEQUENCE": "1",
            "VACCINE_PRODUCT_CODE": "42223111000001107",
            "VACCINE_PRODUCT_TERM": "Quadrivalent influenza vaccine (Sanofi Pasteur)",
            "VACCINE_MANUFACTURER": "Sanofi Pasteur",
            "BATCH_NUMBER": "BN92478105653",
            "EXPIRY_DATE": "20240915",
            "SITE_OF_VACCINATION_CODE": "368209003",
            "SITE_OF_VACCINATION_TERM": "Right arm",
            "ROUTE_OF_VACCINATION_CODE": "1210999013",
            "ROUTE_OF_VACCINATION_TERM": "Intradermal use",
            "DOSE_AMOUNT": dose_amount,
            "DOSE_UNIT_CODE": "2622896019",
            "DOSE_UNIT_TERM": "Inhalation - unit of product usage",
            "INDICATION_CODE": "1037351000000105",
            "LOCATION_CODE": "RJC02",
            "LOCATION_CODE_TYPE_URI": "https://fhir.nhs.uk/Id/ods-organization-code"
        }
        data.append(row)
    df = pd.DataFrame(data)
    timestamp = datetime.now(pytz.UTC).strftime("%Y%m%dT%H%M%S%f")[:-3]
    file_name = f"COVID19_Vaccinations_v5_YGM41_{timestamp}.csv"
    df.to_csv(file_name, index=False, sep="|", quoting=csv.QUOTE_MINIMAL)
    print(f"Generated CSV file: {file_name}")
    return file_name


def upload_file_to_s3(file_name, bucket, prefix):
    """Upload the given file to the specified bucket under the provided prefix."""
    key = f"{prefix}{file_name}"
    with open(file_name, "rb") as f:
        s3_client.put_object(Bucket=bucket, Key=key, Body=f)
    logger.info(f"Uploaded file to s3://{bucket}/{key}")
    return key


def wait_for_ack_file(input_file_name, timeout=120):
    """Poll the ACK_BUCKET for an ack file that contains the input_file_name as a substring."""
    filename_without_ext = input_file_name[:-4] if input_file_name.endswith(".csv") else input_file_name
    search_pattern = f"{ACK_PREFIX}{filename_without_ext}"
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = s3_client.list_objects_v2(Bucket=ACK_BUCKET, Prefix=ACK_PREFIX)
        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]
                if search_pattern in key:
                    print(f"Ack file found: s3://{ACK_BUCKET}/{key}")
                    return key
        time.sleep(5)
    raise Exception(f"Ack file matching '{search_pattern}' not found in bucket {ACK_BUCKET} within {timeout} seconds.")


def get_file_content_from_s3(bucket, key):
    """Download and return the file content from S3."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return content


def check_ack_file_content(content, response_code):
    """Parse the ack CSV file and verify each row's 'HEADER_RESPONSE_CODE' column matches the response code."""
    reader = csv.DictReader(content.splitlines(), delimiter="|")
    rows = list(reader)
    if len(rows) != 3:
        raise Exception(f"Expected 3 rows in the ack file, found {len(rows)}.")
    for i, row in enumerate(rows):
        if "HEADER_RESPONSE_CODE" not in row:
            raise Exception(f"Row {i + 1} does not have a 'HEADER_RESPONSE_CODE' column.")
        if row["HEADER_RESPONSE_CODE"].strip() != response_code:
            raise AssertionError(f"Row {i + 1}: Expected RESPONSE '{response_code}', but found '{row['HEADER_RESPONSE_CODE']}'")
    print("All rows in the ack file have been verified successfully.")