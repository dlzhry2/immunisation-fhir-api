// Define the allowed headers 
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

responseHeaders = Array.isArray(responseHeaders) ? responseHeaders :[];


var headersToRemove = responseHeaders.filter(function(header) {
    return allowedHeaders.indexOf(header) === -1;
});

context.setVariable('debug.headersToRemove', headersToRemove.join(","));

context.setVariable('headersToRemove', headersToRemove.join(","));


