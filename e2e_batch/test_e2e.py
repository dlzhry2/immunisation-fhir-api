
import os
from utils import generate_csv, upload_file_to_s3, get_file_content_from_s3, wait_for_ack_file, check_ack_file_content
from constants import INPUT_BUCKET, INPUT_PREFIX, ACK_BUCKET


def e2e_test_create_success():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content."""
    input_file = generate_csv("PHYLIS", "0.3")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(input_file)
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "OK")

def e2e_test_pre_validation_error():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content."""
    input_file = generate_csv("PHYLIS", "TRUE")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(input_file) 
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "Fatal Error")


def e2e_test_post_validation_error():
    """End-to-end test for generating a CSV, uploading it, and verifying the ack file's content."""
    input_file = generate_csv("", "0.3")
    upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
    os.remove(input_file)
    ack_key = wait_for_ack_file(input_file)
    ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
    check_ack_file_content(ack_content, "Fatal Error")

if __name__ == "__main__":
    e2e_test_create_success()
    e2e_test_post_validation_error()
    e2e_test_pre_validation_error()
