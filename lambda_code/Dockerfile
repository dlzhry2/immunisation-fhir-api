FROM python:3.10-alpine3.18

RUN apk add zip && mkdir -p /lambda_package && mkdir -p /lambda_test && mkdir -p /build
COPY ./src/ /lambda_package/
COPY ./ /lambda_test/
COPY entrypoint.sh /bin/entrypoint.sh
RUN chmod +x /bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
