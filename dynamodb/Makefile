test:
	python -m unittest

test-debug:
	./.venv/bin/pytest -s -v --color=yes -m debug

init:
	terraform init
apply:
	terraform apply -auto-approve


localstack:
	docker run --rm -it -p 4566:4566 -p 4510-4559:4510-4559 localstack/localstack:latest

.PHONY: test test-debug localstack apply init
