# immunisation-fhir-api integration tests

## Running tests locally

- Install and configure `get_token`
  - https://docs.apigee.com/api-platform/system-administration/auth-tools#install
  - https://docs.apigee.com/api-platform/system-administration/using-gettoken
- Open a PR, draft or regular
- Rename `.env.default` to `.env` or merge it with your existing file.
- Rename `.envrc.default` to `.envrc` or merge it with your existing file. These two kept separate so other tools can use `.env` if wanted.
- Set the values in `.env`
- `make run`

To run specific tests you can mark them with the `pytest.mark.debug` decorator and then run `make run-debug`.

Any mark can be used as a filter by putting it after the `-`.


## Troubleshooting

### Tests fail with `No products grant access to proxy [...]`

Products are handled by the infra template and get cleaned up periodically.
Running `/azp run` on the PR should fix it.

### Tests fail with `Invalid Access Token: Ensure APIGEE_ACCESS_TOKEN is valid.`

Try applying the Terraform again. May have been cleaned up by a platforms script.

### Terraform unable to create Cloudwatch Log Group

`Error: creating CloudWatch Logs Log Group (/aws/lambda/imms-pr-66_create_imms): operation error CloudWatch Logs: CreateLogGroup, https response error StatusCode: 400, RequestID: aa314084-220d-44d6-91ac-f6d8b76b428d, ResourceAlreadyExistsException: The specified log group already exists`

The switch from a Lambda package to a Docker image breaks the Log Group creation.
Seemingly because the log groups were not previously part of the state.
Fix by manually deleting the log groups for your workspace before applying the Terraform.
