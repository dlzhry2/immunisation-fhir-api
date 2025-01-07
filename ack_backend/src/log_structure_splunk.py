import os
import json
import time
from datetime import datetime
from functools import wraps
from constants import get_status_code_for_diagnostics
from clients import firehose_client, logger


STREAM_NAME = os.getenv("SPLUNK_FIREHOSE_NAME", "immunisation-fhir-api-internal-dev-splunk-firehose")


def send_log_to_firehose(log_data: dict) -> None:
    """Sends the log_message to Firehose"""
    try:
        record = {"Data": json.dumps({"event": log_data}).encode("utf-8")}
        response = firehose_client.put_record(DeliveryStreamName=STREAM_NAME, Record=record)
        logger.info("Log sent to Firehose: %s", response)  # TODO: Should we be logging full response?
    except Exception as error:  # pylint:disable = broad-exception-caught
        logger.exception("Error sending log to Firehose: %s", error)


def convert_messsage_to_ack_row_logging_decorator(func):
    """This decorator logs the information on the conversion of a single message to an ack data row"""

    @wraps(func)
    def wrapper(message, expected_file_key, expected_created_at_formatted_string):

        base_log_data = {"function_name": f"ack_processor_{func.__name__}", "date_time": str(datetime.now())}
        start_time = time.time()

        try:
            result = func(message, expected_file_key, expected_created_at_formatted_string)

            file_key = message.get("file_key", "file_key_missing")
            message_id = message.get("row_id", "unknown")
            diagnostics = message.get("diagnostics")

            diagnostics_result = process_diagnostics(diagnostics, file_key, message_id)

            log_data = {
                **base_log_data,
                "file_key": file_key,
                "message_id": message.get("row_id", "unknown"),
                "vaccine_type": message.get("vaccine_type", "unknown"),
                "supplier": message.get("supplier", "unknown"),
                "local_id": message.get("local_id", "unknown"),
                "operation_requested": message.get("action_flag", "unknown"),
                "time_taken": f"{round(time.time() - start_time, 5)}s",
                **diagnostics_result,
            }

            try:
                logger.info(f"Function executed successfully: {json.dumps(log_data)}")
                send_log_to_firehose(log_data)
            except Exception:
                logger.warning("Issue with logging")

            return result

        except Exception as e:
            log_data = {
                "status": "fail",
                "statusCode": 500,
                "diagnostics": f"Error converting message to ack row: {str(e)}",
                "date_time": str(datetime.now()),
                "error_source": "convert_message_to_ack_row",
            }
            send_log_to_firehose(log_data)

            raise

    return wrapper


def ack_function_info(func):
    """This decorator logs the execution info for the decorated function and sends it to Splunk."""

    @wraps(func)
    def wrapper(event, context, *args, **kwargs):

        base_log_data = {"function_name": f"ack_processor_{func.__name__}", "date_time": str(datetime.now())}
        start_time = time.time()

        try:
            result = func(event, context, *args, **kwargs)
            return result

        except Exception as e:
            end_time = time.time()
            log_data = {
                **base_log_data,
                "time_taken": f"{round(end_time - start_time, 5)}s",
                "status": "fail",
                "statusCode": 500,
                "diagnostics": f"Error in ack_processor_{func.__name__}: {str(e)}",
            }
            try:
                logger.exception(f"Critical error in function: logging for {func.__name__}")
                send_log_to_firehose(log_data)
            except Exception:
                logger.warning("Issue with logging")

            raise

    return wrapper


def process_diagnostics(diagnostics, file_key, message_id):
    """Returns a dictionary containing the status, statusCode and diagnostics"""
    if diagnostics is not None:
        status_code = get_status_code_for_diagnostics(diagnostics)
        return {"status": "fail", "statusCode": status_code, "diagnostics": diagnostics}

    if file_key == "file_key_missing" or message_id == "unknown":
        diagnostics = "An unhandled error occurred during batch processing"
        return {"status": "fail", "statusCode": 500, "diagnostics": diagnostics}

    return {"status": "success", "statusCode": 200, "diagnostics": "Operation completed successfully"}
