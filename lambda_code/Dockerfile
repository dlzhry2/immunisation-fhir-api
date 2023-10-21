FROM python:3.10-alpine3.18

RUN apk add zip && mkdir -p /lambda && mkdir -p /build
COPY ./src/ /lambda/
COPY entrypoint.sh /bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
