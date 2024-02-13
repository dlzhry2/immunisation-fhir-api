# immunisation-fhir-api lambda

Paths are relative to this directory, `lambda_code`.

## Install dependencies

```shell
pip install poetry
poetry install
```


## Run locally

### Start local DynamoDB

```shell
cd ../devtools
docker compose -f dynamo-compose.yml up -d dynamodb-local
```

DynamoDB uses port 8000 so make sure it's free.


### Create table

Table name here is `local-imms-events` but it can be anything.

```shell
aws dynamodb create-table \
    --endpoint-url http://localhost:8000 \
    --table-name local-imms-events \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=PatientPK,AttributeType=S \
        AttributeName=PatientSK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --table-class STANDARD \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"PatientGSI\",
                \"KeySchema\": [{\"AttributeName\":\"PatientPK\",\"KeyType\":\"HASH\"},
                                {\"AttributeName\":\"PatientSK\",\"KeyType\":\"RANGE\"}],
                \"Projection\":{
                    \"ProjectionType\":\"ALL\"
                },
                \"ProvisionedThroughput\": {
                    \"ReadCapacityUnits\": 10,
                    \"WriteCapacityUnits\": 5
                }
            }
        ]"
```

### Run endpoint

Rename `.envrc.default` to `.envrc` or merge it with your existing file. `direnv` will use them automatically in the terminal.

It contains the following variables:

- `AWS_PROFILE=apim-dev`
- `IMMUNIZATION_ENV=local` 
- `DYNAMODB_TABLE_NAME={table name as created above}`

To run from the terminal: 
```shell
cd src
python get_imms_handler.py 123
```

If not using `.envrc` then:
```shell
cd src
AWS_PROFILE=apim-dev DYNAMODB_TABLE_NAME=local-imms-events IMMUNIZATION_ENV=local python get_imms_handler.py 123
```

### Running tests

- `make test`
- If you want to run specific test, you can try testing one single class or single function with 
  `python -m unittest tests.test_fhir_controller.TestSearchImmunizations        `
  `python -m unittest tests.test_fhir_controller.TestSearchImmunizations.test_search_immunizations`


## Troubleshooting

### Tests fail with `No products grant access to proxy [...]`

Products are handled by the infra template and get cleaned up periodically.
Running `/azp run` on the PR should fix it.


### Terraform unable to create Cloudwatch Log Group

`Error: creating CloudWatch Logs Log Group (/aws/lambda/imms-pr-66_create_imms): operation error CloudWatch Logs: CreateLogGroup, https response error StatusCode: 400, RequestID: aa314084-220d-44d6-91ac-f6d8b76b428d, ResourceAlreadyExistsException: The specified log group already exists`

The switch from a Lambda package to a Docker image breaks the Log Group creation.
Seemingly because the log groups were not previously part of the state.
Fix by manually deleting the log groups for your workspace before applying the Terraform.
