build:
	docker build -t imms-lambda .

package: build
	mkdir -p build
	docker run --rm -v $(shell pwd)/build:/build imms-lambda-build

test2:
	./.venv/bin/pytest -v -s

test:
	python -m unittest
.PHONY: build package
