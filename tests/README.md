# immunisation-fhir-api integration tests

## Running tests locally

- Install and configure `get_token`
  - https://docs.apigee.com/api-platform/system-administration/auth-tools#install
  - https://docs.apigee.com/api-platform/system-administration/using-gettoken
- Open a PR, draft or regular
- Copy `.env.default` to `.env` or merge it with your existing file
  - Set the values for your Apigee user and your PR
- `make run`

If you need to run any pytest commands manually you can set up `direnv` here too.

Just create a `.envrc` with the content `dotenv`. This will import the environment variables from the `.env` file.

E.g. `echo "dotenv" >> .envrc`
