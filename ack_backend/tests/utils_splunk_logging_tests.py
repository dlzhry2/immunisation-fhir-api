from datetime import datetime


class ValidLogging:
    """Logging instances which are both valid and current"""

    fixed_datetime = datetime(2024, 10, 29, 12, 0, 0)

    EMIS_ack_processor_input = {
        "file_key": "RSV_Vaccinations_v5_YGM41_20240905T13005922",
        "row_id": "456",
        "local_id": "local_456",
        "action_flag": "create",
        "imms_id": "4567",
        "created_at_formatted_string": "1223-12-232",
    }
    DPSFULL_ack_processor_input = {
        "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
        "row_id": "123",
        "local_id": "local_123",
        "action_flag": "create",
        "imms_id": "1232",
        "created_at_formatted_string": "1223-12-232",
    }
    EMIS_expected_log_value = {
        "function_name": "lambda_handler",
        "date_time": fixed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success",
        "supplier": "EMIS",
        "file_key": "RSV_Vaccinations_v5_YGM41_20240905T13005922",
        "vaccine_type": "RSV",
        "message_id": "456",
        "operation_requested": "create",
        "time_taken": "3.0s",
        "local_id": "local_456",
        "statusCode": 200,
        "diagnostics": "Operation completed successfully",
    }

    DPSFULL_expected_log_value = {
        "function_name": "lambda_handler",
        "date_time": fixed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success",
        "supplier": "DPSFULL",
        "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
        "vaccine_type": "RSV",
        "message_id": "123",
        "operation_requested": "create",
        "time_taken": "1.0s",
        "local_id": "local_123",
        "statusCode": 200,
        "diagnostics": "Operation completed successfully",
    }
