import logging
import json
import time
from datetime import datetime
from functools import wraps
from log_firehose_splunk import FirehoseLogger
from constants import extract_file_key_elements


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel("INFO")


firehose_logger = FirehoseLogger()


def ack_function_info(func):
    """This decorator logs the execution info for the decorated function and sends it to Splunk."""

    @wraps(func)
    def wrapper(event, context, *args, **kwargs):
        log_data = {
            "function_name": func.__name__,
            "date_time": str(datetime.now()),
            "time_taken": None,
        }

        if event and "Records" in event:
            for record in event["Records"]:
                body_json = record["body"]
                incoming_message_body = json.loads(body_json)
                file_key = incoming_message_body.get("file_key")
                log_data["file_key"] = file_key
                file_key_elements = extract_file_key_elements(file_key)
                log_data["supplier"] = file_key_elements["supplier"]
                log_data["supplier_1"] = incoming_message_body.get("supplier")
                log_data["message_id"] = incoming_message_body.get("row_id")
                log_data["Vaccine_type"] = file_key_elements["vaccine_type"]
                log_data["local_id"] = incoming_message_body.get("local_id")
                log_data["operation_requested"] = incoming_message_body.get("action_flag")
                diagnostics = incoming_message_body.get("diagnostics")
                if diagnostics is None:
                    log_data["statusCode"] = 200
                    log_data["diagnostics"] = "Operation completed successfully"
                    log_data["status"] = "success"
                else:
                    log_data["statusCode"] = get_status_code_for_diagnostics(diagnostics)
                    log_data["diagnostics"] = diagnostics
                    log_data["status"] = "fail"

        start_time = time.time()
        firehose_log = dict()
        try:
            result = func(event, context, *args, **kwargs)
            end_time = time.time()
            log_data["time_taken"] = f"{round(end_time - start_time, 5)}s"

            print(f"logging44444: {json.dumps(log_data)}")
            logger.info(json.dumps(log_data))
            firehose_log["event"] = log_data
            firehose_logger.ack_send_log(firehose_log)

            return result

        except Exception as e:
            log_data["status"] = "fail"
            log_data["statusCode"] = 500
            log_data["diagnostics"] = f"Error in {func.__name__}: {str(e)}"
            end_time = time.time()
            log_data["time_taken"] = f"{round(end_time - start_time, 5)}s"

            logger.exception(json.dumps(log_data))
            firehose_log["event"] = log_data
            firehose_logger.ack_send_log(firehose_log)

            raise

    return wrapper


def get_status_code_for_diagnostics(diagnostics):
    if any(keyword in diagnostics.lower() for keyword in ["unexpected", "unhandled", "internal server"]):
        return 500
    elif diagnostics:
        return 400
    else:
        return 400
