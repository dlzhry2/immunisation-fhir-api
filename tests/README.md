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
