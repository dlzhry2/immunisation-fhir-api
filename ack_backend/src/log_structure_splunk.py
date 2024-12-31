import logging
import os
import json
import time
from datetime import datetime
from functools import wraps
from constants import get_status_code_for_diagnostics
from clients import firehose_client

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel("INFO")

STREAM_NAME = os.getenv("SPLUNK_FIREHOSE_NAME", "immunisation-fhir-api-internal-dev-splunk-firehose")


def send_log_to_firehose(log_data: dict) -> None:
    """Sends the log_message to Firehose"""
    try:
        record = {"Data": json.dumps({"event": log_data}).encode("utf-8")}
        response = firehose_client.put_record(DeliveryStreamName=STREAM_NAME, Record=record)
        logger.info("Log sent to Firehose: %s", response)  # TODO: Should we be logging full response?
    except Exception as error:  # pylint:disable = broad-exception-caught
        logger.exception("Error sending log to Firehose: %s", error)


def ack_function_info(func):
    """This decorator logs the execution info for the decorated function and sends it to Splunk."""

    @wraps(func)
    def wrapper(event, context, *args, **kwargs):
        base_log_data = {"function_name": f"ack_processor_{func.__name__}", "date_time": str(datetime.now())}

        start_time = time.time()
        try:

            if not event or "Records" not in event:
                raise ValueError("No records found in the event")

            for record in event["Records"]:
                try:
                    incoming_message_body = json.loads(record["body"])
                    # TODO: What is the expected structure of incoming_message_body? Is it always a list?
                    # if not isinstance(incoming_message_body, list):
                    #     incoming_message_body = [incoming_message_body]

                    for item in incoming_message_body:
                        print(f"Item: {item}")

                        if not isinstance(item, dict):
                            raise TypeError("Incoming message body is not a dictionary")

                        file_key = item.get("file_key", "file_key_missing")
                        message_id = item.get("row_id", "unknown")
                        diagnostics = item.get("diagnostics")

                        diagnostics_result = process_diagnostics(diagnostics, file_key, message_id)

                        log_data = {
                            **base_log_data,
                            "file_key": file_key,
                            "message_id": message_id,
                            "vaccine_type": item.get("vaccine_type", "unknown"),
                            "supplier": item.get("supplier", "unknown"),
                            "local_id": item.get("local_id", "unknown"),
                            "operation_requested": item.get("action_flag", "unknown"),
                            "time_taken": f"{round(time.time() - start_time, 5)}s",
                            **diagnostics_result,
                        }
                        try:
                            logger.info(f"Function executed successfully: {json.dumps(log_data)}")
                            send_log_to_firehose(log_data)
                        except Exception:
                            logger.warning("Issue with logging")

                except Exception as record_error:
                    try:
                        logger.error(f"Error processing record: {record}. Error: {record_error}")
                        log_data = {
                            "status": "fail",
                            "statusCode": 500,
                            "diagnostics": f"Error processing SQS message: {str(record_error)}",
                            "date_time": str(datetime.now()),
                            "error_source": "ack_lambda_handler",
                        }
                        send_log_to_firehose(log_data)
                    except Exception:
                        logger.warning("Issue with logging")

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
    """Teturns a dictionary containing the status, statusCode and diagnostics"""
    if diagnostics is not None:
        return {
            "status": "fail",
            "statusCode": get_status_code_for_diagnostics(diagnostics),
            "diagnostics": diagnostics,
        }

    if file_key == "file_key_missing" or message_id == "unknown":
        return {
            "status": "fail",
            "statusCode": 500,
            "diagnostics": "An unhandled error happened during batch processing",
        }

    return {"status": "success", "statusCode": 200, "diagnostics": "Operation completed successfully"}
