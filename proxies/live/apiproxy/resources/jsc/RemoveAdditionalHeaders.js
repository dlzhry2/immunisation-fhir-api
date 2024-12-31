
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

var responseHeaders = context.getVariable('response.headers.names');

if(responseHeaders) {
    responseHeaders.forEach(function(header) {
        if (allowedHeaders.indexOf(header) === -1) {
            context.removeVariable('response.header.' + header);
        }
    });
}

