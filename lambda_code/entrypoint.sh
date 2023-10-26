#!/bin/sh

echo "Building lambda package"
cd /lambda || exit 2
pip install -r requirements.txt --target .
zip -qq -r /build/lambda_package.zip .

