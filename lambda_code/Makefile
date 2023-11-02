build:
	docker build -t imms-lambda-build .

package: build
	mkdir -p build
	docker run --rm -v $(shell pwd)/build:/build imms-lambda-build

test:
	DYNAMODB_TABLE_NAME=example-table python -m unittest

.PHONY: build package test
