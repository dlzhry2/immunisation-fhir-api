-include .env

APIGEE_ACCESS_TOKEN ?= $(shell export SSO_LOGIN_URL=https://login.apigee.com && eval get_token -u $(APIGEE_USERNAME))
AWS_DOMAIN_NAME=https://$(shell make -C ../terraform -s output name=service_domain_name)
PYTEST_CMD_INT = APIGEE_ENVIRONMENT=int APIGEE_ACCESS_TOKEN=$(APIGEE_ACCESS_TOKEN) DEFAULT_CLIENT_ID=$(DEFAULT_CLIENT_ID) DEFAULT_CLIENT_SECRET=$(DEFAULT_CLIENT_SECRET)\
	PROXY_NAME=immunisation-fhir-api-int SERVICE_BASE_PATH=immunisation-fhir-api
	poetry run pytest -s -v --color=yes -m smoketest --api-name=immunisation-fhir-api --proxy-name=$PROXY_NAME --apigee-app-id=$(APIGEE_APP_ID) --apigee-organization=nhsd-prod

PYTEST_CMD=APIGEE_ACCESS_TOKEN=$(APIGEE_ACCESS_TOKEN) AWS_DOMAIN_NAME=$(AWS_DOMAIN_NAME) poetry run pytest -s -v --color=yes --api-name=immunisation-fhir-api --proxy-name=$(PROXY_NAME)

run:
	$(PYTEST_CMD)

run-int:
	$(PYTEST_CMD_INT)

run-%:
	$(PYTEST_CMD) -m "$*"





