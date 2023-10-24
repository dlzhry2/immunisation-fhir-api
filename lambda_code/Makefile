build:
	docker build -t imms-lambda .

package: build
	mkdir -p build
	docker run --rm -v $(shell pwd)/build:/build imms-lambda-build

test:
	./.venv/bin/pytest -v -s
.PHONY: build package
