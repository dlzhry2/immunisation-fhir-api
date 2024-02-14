# immunisation-fhir-api integration tests

## Running tests locally

- Install and configure `get_token`
  - https://docs.apigee.com/api-platform/system-administration/auth-tools#install
  - https://docs.apigee.com/api-platform/system-administration/using-gettoken
- Open a PR, draft or regular
- Rename `.envrc.default` to `.envrc` or merge it with your existing file.
- Rename `.env.default` to `.env` or merge it with your existing file.
- Set the values for your Apigee user and your PR in `.env`
- `make run`
