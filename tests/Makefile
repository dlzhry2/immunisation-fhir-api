-include .env
export

APIGEE_ACCESS_TOKEN ?= $(shell export SSO_LOGIN_URL=https://login.apigee.com && eval get_token -u $(APIGEE_USERNAME))
AWS_DOMAIN_NAME=https://$(shell make -C ../terraform -s output name=service_domain_name)
PYTEST_CMD = AWS_DOMAIN_NAME=$(AWS_DOMAIN_NAME) poetry run pytest -s -v --color=yes --api-name=immunisation-fhir-api --proxy-name=$(PROXY_NAME)

run:
	$(PYTEST_CMD)

# run tests with certain marker e.g. make run-sandbox runs tests marked with sandbox
run-%:
	$(PYTEST_CMD) -m "$*"





