# immunisation-fhir-api integration tests

## Running tests locally

- Install and configure `get_token`
  - https://docs.apigee.com/api-platform/system-administration/auth-tools#install
  - https://docs.apigee.com/api-platform/system-administration/using-gettoken
- Open a PR
- Create a `.env` file like the following:

```bash
APIGEE_USERNAME={your username}
PROXY_NAME=immunisation-fhir-api-pr-{pr number}
APIGEE_ENVIRONMENT=internal-dev
SERVICE_BASE_PATH=immunisation-fhir-api-pr-{pr number}
SOURCE_COMMIT_ID=3bdc821db6d56e7215c9be37ee005482475f8a14 # TODO
```

- `make run`
