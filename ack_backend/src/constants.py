"""Constants for ack lambda"""


class Constants:
    """Constants for ack lambda"""

    ack_headers = [
        "MESSAGE_HEADER_ID",
        "HEADER_RESPONSE_CODE",
        "ISSUE_SEVERITY",
        "ISSUE_CODE",
        "ISSUE_DETAILS_CODE",
        "RESPONSE_TYPE",
        "RESPONSE_CODE",
        "RESPONSE_DISPLAY",
        "RECEIVED_TIME",
        "MAILBOX_FROM",
        "LOCAL_ID",
        "IMMS_ID",
        "OPERATION_OUTCOME",
        "MESSAGE_DELIVERY",
    ]

    error_code_mapping = {
        500: ["application includes invalid authorization values", "unhandled", "server error"],
        422: ["duplicate", "duplicated"],
        403: ["unauthorized"],
        404: ["not found", "does not exist"],
        204: ["deleted", "No content"],
    }


def get_status_code_for_diagnostics(diagnostics_message: str) -> int:
    """Returns the status_code for diagnostics"""
    diagnostics_message = diagnostics_message.lower()

    default_error_code = 500

    for error_code, keywords in Constants.error_code_mapping.items():
        for keyword in keywords:
            if keyword in diagnostics_message:
                return error_code
    return default_error_code
