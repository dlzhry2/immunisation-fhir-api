test:
	./.venv/bin/pytest -s -v --color=yes

test-debug:
	./.venv/bin/pytest -s -v --color=yes -m debug

init:
	terraform init
apply:
	terraform apply -auto-approve

.PHONY: test test-debug
