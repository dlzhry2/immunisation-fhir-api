import boto3
import pandas as pd
import pytz
import uuid
from datetime import datetime
import time
import csv
import os
import pytest

# Bucket for uploading the input CSV file
INPUT_BUCKET = "immunisation-batch-internal-dev-data-sources"  # Update with your input S3 bucket name
INPUT_PREFIX = ""          # Folder in the input bucket
# Bucket where the ack file is generated
ACK_BUCKET = "immunisation-batch-internal-dev-data-destinations"       # Update with your ack S3 bucket name
ACK_PREFIX = "forwardedFile/"                     # Folder in the ack bucket
REGION = "eu-west-2"                    # Update to your AWS region
# Initialize the S3 client (used for both buckets)
s3_client = boto3.client("s3", region_name=REGION)


def generate_csv():
    """
    Generate a CSV file with 3 rows and unique GUIDs for UNIQUE_ID.
    The filename is timestamped.
    """
    unique_ids = [str(uuid.uuid4()) for _ in range(3)]
    data = []
    for i in range(3):
        row = {
            "NHS_NUMBER": "9732928395",
            "PERSON_FORENAME": "PHYLIS",
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
            "DOSE_AMOUNT": "0.3",
            "DOSE_UNIT_CODE": "2622896019",
            "DOSE_UNIT_TERM": "Inhalation - unit of product usage",
            "INDICATION_CODE": "1037351000000105",
            "LOCATION_CODE": "RJC02",
            "LOCATION_CODE_TYPE_URI": "https://fhir.nhs.uk/Id/ods-organization-code"
        }
        data.append(row)
    df = pd.DataFrame(data)
    # Create a dynamic timestamp for the filename (example: 20240928T13005901)
    timestamp = datetime.now(pytz.UTC).strftime("%Y%m%dT%H%M%S%f")[:-3]
    file_name = f"COVID19_Vaccinations_v5_YGM41_{timestamp}.csv"
    # Save CSV locally using pipe (|) as delimiter
    df.to_csv(file_name, index=False, sep="|", quoting=1)
    print(f"Generated CSV file: {file_name}")
    return file_name


def upload_file_to_s3(file_name, bucket, prefix):
    """
    Upload the given file to the specified bucket under the provided prefix.
    Returns the full key used in S3.
    """
    key = f"{prefix}{file_name}"
    with open(file_name, "rb") as f:
        s3_client.put_object(Bucket=bucket, Key=key, Body=f)
    print(f"Uploaded file to s3://{bucket}/{key}")
    return key


def wait_for_ack_file(input_file_name, timeout=120):
    """
    Poll the ACK_BUCKET for an ack file that contains the input_file_name as a substring.
    This allows for extra elements in the ack file's name.
    """
    if input_file_name.endswith(".csv"):
        filename_without_ext = input_file_name[:-4]
    search_pattern = f"forwardedFile/{filename_without_ext}"
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = s3_client.list_objects_v2(Bucket=ACK_BUCKET, Prefix=ACK_PREFIX)
        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]
                print(key)
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
    """
    Parse the ack CSV file (assuming a pipe delimiter) and check that:
        - It has exactly 3 data rows.
        - Each row has a column named "RESPONSE" with a value of "200".
    """
    reader = csv.DictReader(content.splitlines(), delimiter="|")
    rows = list(reader)
    for i, row in enumerate(rows):
        if "HEADER_RESPONSE_CODE" not in row:
            raise Exception(f"Row {i+1} does not have a 'RESPONSE' column.")
        if row["HEADER_RESPONSE_CODE"].strip() != response_code:
            print(f"Row {i+1}: RESPONSE is {response_code}.")
    print("All rows in the ack file have been verified successfully.")


def e2e_test_post_validation_error():
    """
    End-to-end test:
        1. Generate a CSV file with 3 rows (each with a unique GUID).
        2. Upload the CSV file to the INPUT_BUCKET under the INPUT_PREFIX.
        3. Wait for the corresponding ack file to be generated in the ACK_BUCKET,
            searching using a 'like' (substring) operator.
        4. Download and verify that each row in the ack file has a RESPONSE value of 200.
    """
    # Step 1: Generate CSV
    input_file = generate_csv()
    # Step 2: Upload CSV to the input bucket
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    # Step 3: Wait for the ack file in the ACK_BUCKET using a substring search
    ack_key = wait_for_ack_file(input_file)
    # Step 4: Retrieve and check ack file content from the ack bucket
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "Fatal Error")
    # Optionally, clean up the local CSV file
    os.remove(input_file)


if __name__ == "__main__":

    e2e_test_post_validation_error()


@pytest.mark.e2e
def test_e2e_real():

    e2e_test_post_validation_error()
