test:
	python -m unittest

test-debug:
	./.venv/bin/pytest -s -v --color=yes -m debug

delete-table:
	aws dynamodb delete-table --table-name local-imms-events --region us-east-1 --endpoint-url http://localhost:4566

init:
	terraform init
apply:
	terraform apply -auto-approve


localstack:
	docker run --rm -it -p 4566:4566 -p 4510-4559:4510-4559 localstack/localstack:latest

.PHONY: test test-debug localstack apply init
