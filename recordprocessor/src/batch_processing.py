"""Functions for processing the file on a row-by-row basis"""

import json
import os
import time
import logging
import uuid
from constants import Constants
from utils_for_recordprocessor import get_csv_content_dict_reader
from unique_permission import get_unique_action_flags_from_s3
from make_and_upload_ack_file import make_and_upload_ack_file
from get_operation_permissions import get_operation_permissions
from models.errors import Severity, Code, create_operation_outcome
from process_row import process_row
from mappings import Vaccine
from fhir_controller import FhirController, make_controller

logging.basicConfig(level="INFO")
logger = logging.getLogger()


def process_csv_to_fhir(incoming_message_body: dict) -> None:
    """
    For each row of the csv, attempts to transform into FHIR format, sends a message to kinesis,
    and documents the outcome for each row in the ack file.
    """
    logger.info("Event: %s", incoming_message_body)

    # Get details needed to process file
    file_id = incoming_message_body.get("message_id")
    vaccine: Vaccine = next(  # Convert vaccine_type to Vaccine enum
        vaccine
        for vaccine in Vaccine
        if vaccine.value == incoming_message_body.get("vaccine_type").upper()
    )
    supplier = incoming_message_body.get("supplier").upper()
    file_key = incoming_message_body.get("filename")
    permission = incoming_message_body.get("permission")
    created_at_formatted_string = incoming_message_body.get(
        "created_at_formatted_string"
    )
    allowed_operations = get_operation_permissions(vaccine, permission)

    # Fetch the data
    bucket_name = os.getenv("SOURCE_BUCKET_NAME")
    csv_reader, csv_data = get_csv_content_dict_reader(bucket_name, file_key)

    is_valid_headers = validate_content_headers(csv_reader)
    # Validate has permission to perform at least one of the requested actions
    action_flag_check = validate_action_flag_permissions(
        supplier, vaccine.value, permission, csv_data
    )

    if not action_flag_check or not is_valid_headers:
        make_and_upload_ack_file(
            file_id, file_key, False, False, created_at_formatted_string
        )
    else:
        make_and_upload_ack_file(
            file_id, file_key, True, True, created_at_formatted_string
        )

        row_count = 0  # Initialize a counter for rows
        for row in csv_reader:
            row_count += 1
            row_id = f"{file_id}#{row_count}"
            logger.info("MESSAGE ID : %s", row_id)
            # Process the row to obtain the details needed for the message_body and ack file
            details_from_processing = process_row(vaccine, allowed_operations, row)

            create_immunization(details_from_processing, supplier, make_controller())
        logger.info("Total rows processed: %s", row_count)


def create_immunization(immunisation: any, supplier: str, controller: FhirController):
    try:
        return controller.create_immunization(immunisation, supplier)
    except Exception as e:
        exp_error = create_operation_outcome(
            resource_id=str(uuid.uuid4()), severity=Severity.error, code=Code.server_error, diagnostics=str(e)
        )
        return FhirController.create_response(500, exp_error)


def validate_content_headers(csv_content_reader):
    """Returns a bool to indicate whether the given CSV headers match the 34 expected headers exactly"""
    return csv_content_reader.fieldnames == Constants.expected_csv_headers


def validate_action_flag_permissions(
    supplier: str, vaccine_type: str, permission, csv_data
) -> bool:
    """
    Returns True if the supplier has permission to perform ANY of the requested actions for the given vaccine type,
    else False.
    """
    # Obtain the allowed permissions for the supplier
    allowed_permissions_set = permission
    # If the supplier has full permissions for the vaccine type, return True
    if f"{vaccine_type}_FULL" in allowed_permissions_set:
        return True

    # Get unique ACTION_FLAG values from the S3 file
    operations_requested = get_unique_action_flags_from_s3(csv_data)

    # Convert action flags into the expected operation names
    operation_requests_set = {
        f"{vaccine_type}_{'CREATE' if action == 'NEW' else action}"
        for action in operations_requested
    }

    # Check if any of the CSV permissions match the allowed permissions
    if operation_requests_set.intersection(allowed_permissions_set):
        logger.info(
            "%s permissions %s match one of the requested permissions required to %s",
            supplier,
            allowed_permissions_set,
            operation_requests_set,
        )
        return True

    return False


def main(event: str) -> None:
    """Process each row of the file"""
    logger.info("task started")
    start = time.time()
    try:
        process_csv_to_fhir(incoming_message_body=json.loads(event))
    except Exception as error:  # pylint: disable=broad-exception-caught
        logger.error("Error processing message: %s", error)
    end = time.time()
    print(f"Total time for completion:{round(end - start, 5)}s")


if __name__ == "__main__":
    main(event=os.environ.get("EVENT_DETAILS"))
