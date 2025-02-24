import time
import csv
import pandas as pd
import uuid
from io import StringIO
from datetime import datetime, timezone
from clients import logger, s3_client, table
from errors import AckFileNotFoundError, DynamoDBMismatchError
from constants import ACK_BUCKET, FORWARDEDFILE_PREFIX, SOURCE_BUCKET


def generate_csv(file_name, fore_name, dose_amount, action_flag):
    """
    Generate a CSV file with 2 rows.
    - For `CREATE`, both rows have unique `UNIQUE_ID` with `"ACTION_FLAG": "NEW"`.
    - For `UPDATE`, one row has `"ACTION_FLAG": "NEW"` and the other `"ACTION_FLAG": "UPDATE"` with the same `UNIQUE_ID`.
    - For `DELETE`, one row has `"ACTION_FLAG": "NEW"` and the other `"ACTION_FLAG": "DELETE"` with the same `UNIQUE_ID`.
    """
    data = []

    if action_flag == "CREATE":
        unique_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        for unique_id in unique_ids:
            data.append(create_row(unique_id, fore_name, dose_amount, "NEW"))
    elif action_flag == "UPDATE":
        unique_id = str(uuid.uuid4())
        data.append(create_row(unique_id, fore_name, dose_amount, "NEW"))
        data.append(create_row(unique_id, fore_name, dose_amount, "UPDATE"))
    elif action_flag == "DELETE":
        unique_id = str(uuid.uuid4())
        data.append(create_row(unique_id, fore_name, dose_amount, "NEW"))
        data.append(create_row(unique_id, fore_name, dose_amount, "DELETE"))

    df = pd.DataFrame(data)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")[:-3]
    file_name = (
        f"COVID19_Vaccinations_v4_YGM41_{timestamp}.csv"
        if file_name
        else f"COVID19_Vaccinations_v5_YGM41_{timestamp}.csv"
    )
    df.to_csv(file_name, index=False, sep="|", quoting=csv.QUOTE_MINIMAL)
    return file_name


def create_row(unique_id, fore_name, dose_amount, action_flag):
    """Helper function to create a single row with the specified UNIQUE_ID and ACTION_FLAG."""
    return {
        "NHS_NUMBER": "9732928395",
        "PERSON_FORENAME": fore_name,
        "PERSON_SURNAME": "James",
        "PERSON_DOB": "20080217",
        "PERSON_GENDER_CODE": "0",
        "PERSON_POSTCODE": "WD25 0DZ",
        "DATE_AND_TIME": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"),
        "SITE_CODE": "RVVKC",
        "SITE_CODE_TYPE_URI": "https://fhir.nhs.uk/Id/ods-organization-code",
        "UNIQUE_ID": unique_id,
        "UNIQUE_ID_URI": "https://www.ravs.england.nhs.uk/",
        "ACTION_FLAG": action_flag,
        "PERFORMING_PROFESSIONAL_FORENAME": "PHYLIS",
        "PERFORMING_PROFESSIONAL_SURNAME": "James",
        "RECORDED_DATE": datetime.now(timezone.utc).strftime("%Y%m%d"),
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
        "LOCATION_CODE_TYPE_URI": "https://fhir.nhs.uk/Id/ods-organization-code",
    }


def upload_file_to_s3(file_name, bucket, prefix):
    """Upload the given file to the specified bucket under the provided prefix."""
    key = f"{prefix}{file_name}"
    with open(file_name, "rb") as f:
        s3_client.put_object(Bucket=bucket, Key=key, Body=f)
    return key


def wait_for_ack_file(ack_prefix, input_file_name, timeout=120):
    """Poll the ACK_BUCKET for an ack file that contains the input_file_name as a substring."""
    filename_without_ext = input_file_name[:-4] if input_file_name.endswith(".csv") else input_file_name
    search_pattern = f"{ack_prefix if ack_prefix else FORWARDEDFILE_PREFIX}{filename_without_ext}"
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = s3_client.list_objects_v2(
            Bucket=ACK_BUCKET, Prefix=ack_prefix if ack_prefix else FORWARDEDFILE_PREFIX
        )
        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]
                if search_pattern in key:
                    return key
        time.sleep(5)
    raise AckFileNotFoundError(
        f"Ack file matching '{search_pattern}' not found in bucket {ACK_BUCKET} within {timeout} seconds."
    )


def get_file_content_from_s3(bucket, key):
    """Download and return the file content from S3."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return content


def check_ack_file_content(content, response_code, operation_outcome, operation_requested):
    """Parse the acknowledgment (ACK) CSV file and verify its content."""
    reader = csv.DictReader(content.splitlines(), delimiter="|")
    rows = list(reader)
    for i, row in enumerate(rows):
        validate_header_response_code(row, i, response_code)
        if row["HEADER_RESPONSE_CODE"].strip() == "Fatal Error":
            validate_fatal_error(row, i, operation_outcome)
        if row["HEADER_RESPONSE_CODE"].strip() == "OK":
            validate_ok_response(row, i, operation_requested)


def validate_header_response_code(row, index, expected_code):
    """Ensure HEADER_RESPONSE_CODE exists and matches expected response code."""
    if "HEADER_RESPONSE_CODE" not in row:
        raise ValueError(f"Row {index + 1} does not have a 'HEADER_RESPONSE_CODE' column.")
    if row["HEADER_RESPONSE_CODE"].strip() != expected_code:
        raise ValueError(
            f"Row {index + 1}: Expected RESPONSE '{expected_code}', but found '{row['HEADER_RESPONSE_CODE']}'"
        )


def validate_fatal_error(row, index, expected_outcome):
    """Ensure OPERATION_OUTCOME matches expected outcome for Fatal Error responses."""
    if row["OPERATION_OUTCOME"].strip() != expected_outcome:
        raise ValueError(
            f"Row {index + 1}: Expected RESPONSE '{expected_outcome}', but found '{row['OPERATION_OUTCOME']}'"
        )


def validate_ok_response(row, index, operation_requested):
    """Validate LOCAL_ID format and verify PK and operation match from DynamoDB for OK responses."""
    if "LOCAL_ID" not in row:
        raise ValueError(f"Row {index + 1} does not have a 'LOCAL_ID' column.")
    identifier_pk = extract_identifier_pk(row, index)
    dynamo_pk, operation = fetch_pk_and_operation_from_dynamodb(identifier_pk)
    if dynamo_pk != row["IMMS_ID"]:
        raise DynamoDBMismatchError(
            f"Row {index + 1}: Mismatch - DynamoDB PK '{dynamo_pk}' does not match ACK file IMMS_ID '{row['IMMS_ID']}'"
        )
    if operation != operation_requested:
        raise DynamoDBMismatchError(
            (
                f"Row {index + 1}: Mismatch - DynamoDB Operation '{operation}' "
                f"does not match operation requested '{operation_requested}'"
            )
        )


def extract_identifier_pk(row, index):
    """Extract LOCAL_ID and convert to IdentifierPK."""
    try:
        local_id, unique_id_uri = row["LOCAL_ID"].split("^")
        return f"{unique_id_uri}#{local_id}"
    except ValueError:
        raise AssertionError(f"Row {index + 1}: Invalid LOCAL_ID format - {row['LOCAL_ID']}")


def fetch_pk_and_operation_from_dynamodb(identifier_pk):
    """Fetch PK and operation with IdentifierPK as the query key."""
    try:
        response = table.query(
            IndexName="IdentifierGSI",
            KeyConditionExpression="IdentifierPK = :identifier_pk",
            ExpressionAttributeValues={":identifier_pk": identifier_pk},
        )
        if "Items" in response and response["Items"]:
            return (
                response["Items"][0]["PK"],
                response["Items"][0]["Operation"],
            )
        else:
            return "NOT_FOUND"

    except Exception as e:
        logger.error(f"Error fetching from DynamoDB: {e}")
        return "ERROR"


def validate_row_count(source_file_name, ack_file_name):
    """
    Compare the row count of a file in one S3 bucket with a file in another S3 bucket.
    Raises:
        AssertionError: If the row counts do not match.
    """
    source_file_row_count = fetch_row_count(SOURCE_BUCKET, f"archive/{source_file_name}")
    ack_file_row_count = fetch_row_count(ACK_BUCKET, ack_file_name)
    assert (
        source_file_row_count == ack_file_row_count
    ), f"Row count mismatch: Input ({source_file_row_count}) vs Ack ({ack_file_row_count})"


def fetch_row_count(bucket, file_name):
    "Fetch the row count for the file from the s3 bucket"

    response_input = s3_client.get_object(Bucket=bucket, Key=file_name)
    content_input = response_input["Body"].read().decode("utf-8")
    return sum(1 for _ in csv.reader(StringIO(content_input)))
