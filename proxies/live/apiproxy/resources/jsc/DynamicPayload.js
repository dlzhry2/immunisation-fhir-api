var response = JSON.parse(context.getVariable("response.content"));

var diagnosticsMessage = "";
if (response.statusCode === 422) {
    diagnosticsMessage = "Submitted resource is not valid.";
} else if (response.statusCode === 500) {
    diagnosticsMessage = "Unexpected internal server error.";
}

var dynamicPayload = {
    "resourceType": "OperationOutcome",
    "id": response.id,
    "meta": {
        "profile": [
            "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
        ]
    },
    "issue": [
        {
            "severity": "error",
            "code": response.issue[0].code,
            "details": {
                "coding": [
                    {
                        "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                        "code": response.issue[0].code
                    }
                ]
            },
            "diagnostics": diagnosticsMessage
        }
    ]
};

context.setVariable("dynamicPayload", JSON.stringify(dynamicPayload));