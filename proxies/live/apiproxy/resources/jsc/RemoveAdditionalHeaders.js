
var allowedHeaders = [
    'Date',
    'Content-Type',
    'Content-Length',
    'Connection',
    'X-Correlation-ID',
    'X-Request-ID',
    'Accept',
    'Strict-Transport-Security'
];

var requestHeaders = context.getVariable('request.headers.names');

if(requestHeaders) {
    requestHeaders.forEach(function(header) {
        if (allowedHeaders.indexOf(header) === -1) {
            context.removeVariable('request.header.' + header);
        }
    });
}

