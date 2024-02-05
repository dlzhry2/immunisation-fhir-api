#First Stage
FROM alpine:latest
#Installing Jq
RUN apk add jq
#Copying OAS spec file in container
COPY "immunisation-fhir-api.json" ./
#Copyign HeslthStatus OAS file in container
COPY "HealthStatusEndpoint.json" ./
#Copying whole specification directory , to get inline examples and schemas
COPY ./specification ./specification
#Adding Health status endpoint to main spec file
RUN jq ".paths+=$(cat HealthStatusEndpoint.json)" immunisation-fhir-api.json > updated-spec.json


#Second stage
FROM stoplight/prism:4
#Inheriting from previous image and copying updated OAS spec file to current container
COPY --from=0  /specification  /usr/src/prism/packages/cli/immunisation-fhir-api/specification
COPY --from=0  /updated-spec.json  /usr/src/prism/packages/cli/immunisation-fhir-api/specification/immunisation-fhir-api.json

#Running command of mock with OAS file
CMD ["mock" , "-h", "0.0.0.0", "-p" ,"9000" ,"immunisation-fhir-api/specification/immunisation-fhir-api.json"]
