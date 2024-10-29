// extract version from Accept header
function extractVersion() {
    var acceptHeader = context.getVariable("request.header.Accept");
    var versionPattern = /application\/fhir\+json;\s*version=(\d+)/i;
    var match = acceptHeader.match(versionPattern);
    var version = match ? match[1] : "1"; // Default to version 1 if not provided
    context.setVariable("version", version);
}

extractVersion();
