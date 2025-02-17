import os
import unittest
from utils import (
    generate_csv,
    upload_file_to_s3,
    get_file_content_from_s3,
    wait_for_ack_file,
    check_ack_file_content,
)
from constants import INPUT_BUCKET, INPUT_PREFIX, ACK_BUCKET, PRE_VALIDATION_ERROR, POST_VALIDATION_ERROR


class TestE2EBatch(unittest.TestCase):

    def test_create_success(self):
        """Test CREATE scenario."""
        input_file = generate_csv(False, "PHYLIS", "0.3", action_flag="CREATE")
        upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
        os.remove(input_file)
        ack_key = wait_for_ack_file(None, input_file)
        ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
        check_ack_file_content(ack_content, "OK", None)

    def test_update_success(self):
        """Test UPDATE scenario."""
        input_file = generate_csv(False, "PHYLIS", "0.5", action_flag="UPDATE")
        upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
        os.remove(input_file)
        ack_key = wait_for_ack_file(None, input_file)
        ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
        check_ack_file_content(ack_content, "OK", None)

    def test_delete_success(self):
        """Test DELETE scenario."""
        input_file = generate_csv(False, "PHYLIS", "0.8", action_flag="DELETE")
        upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
        os.remove(input_file)
        ack_key = wait_for_ack_file(None, input_file)
        ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
        check_ack_file_content(ack_content, "OK", None)

    def test_pre_validation_error(self):
        """Test pre-validation error scenario."""
        input_file = generate_csv(False, "PHYLIS", "TRUE", action_flag="CREATE")
        upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
        os.remove(input_file)
        ack_key = wait_for_ack_file(None, input_file)
        ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
        check_ack_file_content(ack_content, "Fatal Error", PRE_VALIDATION_ERROR)

    def test_post_validation_error(self):
        """Test post-validation error scenario."""
        input_file = generate_csv(False, "", "0.3", action_flag="CREATE")
        upload_file_to_s3(input_file, INPUT_BUCKET, INPUT_PREFIX)
        os.remove(input_file)
        ack_key = wait_for_ack_file(None, input_file)
        ack_content = get_file_content_from_s3(ACK_BUCKET, ack_key)
        check_ack_file_content(ack_content, "Fatal Error", POST_VALIDATION_ERROR)

if __name__ == "__main__":
    unittest.main()
