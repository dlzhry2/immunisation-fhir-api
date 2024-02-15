-include .env

APIGEE_ACCESS_TOKEN ?= $(shell export SSO_LOGIN_URL=https://login.apigee.com && eval get_token -u $(APIGEE_USERNAME))
AWS_DOMAIN_NAME=https://$(shell make -C ../terraform -s output name=service_domain_name || true)

cmd = APIGEE_ACCESS_TOKEN=$(APIGEE_ACCESS_TOKEN) APIGEE_USERNAME=$(APIGEE_USERNAME) poetry run python -m unittest
run:
	$(cmd)

run-int:
	$(PYTEST_CMD_INT)

run-%:
	$(PYTEST_CMD) -m "$*"





