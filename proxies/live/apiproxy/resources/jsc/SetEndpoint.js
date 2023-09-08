var endpoint=context.getVariable('endpoint');
const pathSuffix = context.getVariable("proxy.pathsuffix")
const queryString = context.getVariable("request.querystring")

if (endpoint) {
  url = endpoint + pathSuffix
  if (queryString !== "") {
    url = url + queryString
  }
  context.setVariable("target.url", url)

} else {
  context.setVariable("endpointNotFound", true)
}


