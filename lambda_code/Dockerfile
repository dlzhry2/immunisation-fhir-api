FROM python:3.9

RUN apt update && apt upgrade -y && apt install -y zip

RUN mkdir -p /lambda_package && mkdir -p /lambda_test && mkdir -p /build
COPY ./src/ ./requirements.txt ./requirements_binary.txt /lambda_package/
COPY ./ /lambda_test/
COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
