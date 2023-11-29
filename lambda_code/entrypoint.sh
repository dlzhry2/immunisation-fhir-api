#!/usr/bin/bash
set -eo pipefail

cd /lambda_test || exit 2
echo "Installing dependencies for test..."
pip install -q -r requirements.txt
echo "Running unit tests"
export DYNAMODB_TABLE_NAME=example_table
python -m unittest

cd /lambda_package || exit 2
echo "Installing main dependencies..."
pip install -q -r requirements.txt --target .
echo "Building cryptography layer"
pip install \
--platform manylinux2014_x86_64 \
--target=. \
--implementation cp \
--python-version 3.10 \
--only-binary=:all: --upgrade \
'cryptography==36.0.1'
echo "Building lambda package"
zip -qq -r /build/lambda_package.zip .
echo "Done!"

