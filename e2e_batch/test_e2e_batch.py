import os
from utils import (
    generate_csv,
    upload_file_to_s3,
    get_file_content_from_s3,
    wait_for_ack_file,
    check_ack_file_content,
)
from constants import INPUT_BUCKET, INPUT_PREFIX, ACK_BUCKET
from clients import logger


def e2e_test_create_success():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content (CREATE scenario)."""
    input_file = generate_csv(False, "PHYLIS", "0.3", action_flag="CREATE")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(None, input_file)
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "OK")
    logger.info("Test e2e_test_create_success successfully passed")


def e2e_test_update_success():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content (UPDATE scenario)."""
    input_file = generate_csv(False, "PHYLIS", "0.5", action_flag="UPDATE")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(None, input_file)
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "OK")
    logger.info("Test e2e_test_update_success successfully passed")


def e2e_test_delete_success():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content (DELETE scenario)."""
    input_file = generate_csv(False, "PHYLIS", "0.8", action_flag="DELETE")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(None, input_file)
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "OK")
    logger.info("Test e2e_test_delete_success successfully passed")


def e2e_test_pre_validation_error():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content."""
    input_file = generate_csv(False, "PHYLIS", "TRUE", action_flag="CREATE")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(None, input_file)
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "Fatal Error")
    logger.info("Test e2e_test_pre_validation_error successfully passed")


def e2e_test_post_validation_error():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content."""
    input_file = generate_csv(False, "", "0.3", action_flag="CREATE")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(None, input_file)
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "Fatal Error")
    logger.info("Test e2e_test_post_validation_error successfully passed")


if __name__ == "__main__":
    e2e_test_create_success()
    e2e_test_update_success()
    e2e_test_delete_success()
    e2e_test_pre_validation_error()
    e2e_test_post_validation_error()
