build:
	docker build -t mesh-lambda-build .

package: build
	mkdir -p build
	docker run --rm -v $(shell pwd)/build:/build mesh-lambda-build

.PHONY: build package 
