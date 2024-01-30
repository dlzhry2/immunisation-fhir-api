# immunisation-fhir-api lambda

## Install dependencies

`poetry install`


## Troubleshooting

### Tests fail with `No products grant access to proxy [...]`

Products are handled by the infra template and get cleaned up periodically.
Running `/azp run` on the PR should fix it.


### Terraform unable to create Cloudwatch Log Group

`Error: creating CloudWatch Logs Log Group (/aws/lambda/imms-pr-66_create_imms): operation error CloudWatch Logs: CreateLogGroup, https response error StatusCode: 400, RequestID: aa314084-220d-44d6-91ac-f6d8b76b428d, ResourceAlreadyExistsException: The specified log group already exists`

The switch from a Lambda package to a Docker image breaks the Log Group creation.
Seemingly because the log groups were not previously part of the state.
Fix by manually deleting the log groups for your workspace before applying the Terraform.
