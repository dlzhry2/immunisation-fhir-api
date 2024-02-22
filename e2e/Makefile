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

file = immunisation-fhir-api-local
key-pair:
	#ssh-keygen -t rsa -b 4096 -m PEM -E SHA512 -f .keys/immunisation-fhir-api-local.key -N ""
	#openssl rsa -in  .keys/immunisation-fhir-api-local.key -pubout -outform PEM -out .keys/immunisation-fhir-api-local.key.pub
	openssl genrsa -out .keys/$(file).key 4096
	openssl rsa -in .keys/$(file).key -pubout -outform PEM -out .keys/$(file).key.pub



