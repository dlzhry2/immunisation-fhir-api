import json

ALLOWED_METHODS = ["GET", "POST", "DELETE", "PUT"]


def not_found_handler(event, context):

    if event.get("httpMethod") not in ALLOWED_METHODS:
        response = {
            "statusCode": 405,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {
                    "resourceType": "OperationOutcome",
                    "id": "a5abca2a-4eda-41da-b2cc-95d48c6b791d",
                    "meta": {
                        "profile": [
                            "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
                        ]
                    },
                    "issue": [
                        {
                            "severity": "error",
                            "code": "not-supported",
                            "details": {
                                "coding": [
                                    {
                                        "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                                        "code": "NOT_SUPPORTED",
                                    }
                                ]
                            },
                            "diagnostics": "Method Not Allowed",
                        }
                    ],
                }
            ),
        }
        return response

    else:
        response = {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {
                    "resourceType": "OperationOutcome",
                    "id": "a5abca2a-4eda-41da-b2cc-95d48c6b791d",
                    "meta": {
                        "profile": [
                            "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
                        ]
                    },
                    "issue": [
                        {
                            "severity": "error",
                            "code": "not-found",
                            "details": {
                                "coding": [
                                    {
                                        "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                                        "code": "NOT_FOUND",
                                    }
                                ]
                            },
                            "diagnostics": "The requested resource was not found.",
                        }
                    ],
                }
            ),
        }
        return response
