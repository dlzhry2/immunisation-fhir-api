import urllib.parse

import pprint

import json
import os
import re
import uuid
from typing import Optional
from decimal import Decimal

import boto3
import base64
from botocore.config import Config
from aws_lambda_typing.events import APIGatewayProxyEventV1

from cache import Cache
from fhir_repository import ImmunizationRepository, create_table
from fhir_service import FhirService, UpdateOutcome, get_service_url
from models.errors import (
    Severity,
    Code,
    create_operation_outcome,
    ResourceNotFoundError,
    UnhandledResponseError,
    ValidationError,
    IdentifierDuplicationError
)
from pds_service import PdsService, Authenticator
from urllib.parse import parse_qs


def make_controller(
    pds_env: str = os.getenv("PDS_ENV", "int"),
    immunization_env: str = os.getenv("IMMUNIZATION_ENV")
):
    endpoint_url = "http://localhost:4566" if immunization_env == "local" else None
    imms_repo = ImmunizationRepository(create_table(endpoint_url=endpoint_url))
    boto_config = Config(region_name="eu-west-2")
    cache = Cache(directory="/tmp")
    authenticator = Authenticator(
        boto3.client("secretsmanager", config=boto_config), pds_env, cache
    )
    pds_service = PdsService(authenticator, pds_env)

    service = FhirService(imms_repo=imms_repo, pds_service=pds_service)

    return FhirController(fhir_service=service)


class FhirController:
    immunization_id_pattern = r"^[A-Za-z0-9\-.]{1,64}$"

    def __init__(self, fhir_service: FhirService):
        self.fhir_service = fhir_service

    def get_immunization_by_id(self, aws_event) -> dict:
        imms_id = aws_event["pathParameters"]["id"]

        id_error = self._validate_id(imms_id)
        if id_error:
            return self.create_response(400, id_error)

        resource = self.fhir_service.get_immunization_by_id(imms_id)
        if resource:
            return FhirController.create_response(200, resource.json())
        else:
            msg = "The requested resource was not found."
            id_error = create_operation_outcome(
                resource_id=str(uuid.uuid4()),
                severity=Severity.error,
                code=Code.not_found,
                diagnostics=msg,
            )
            return FhirController.create_response(404, id_error)

    def create_immunization(self, aws_event):
        try:
            imms = json.loads(aws_event["body"], parse_float=Decimal)
        except json.decoder.JSONDecodeError as e:
            return self._create_bad_request(
                f"Request's body contains malformed JSON: {e}"
            )

        try:
            resource = self.fhir_service.create_immunization(imms)
            location = f"{get_service_url()}/Immunization/{resource.id}"
            return self.create_response(201, None, {"Location": location})
        except ValidationError as error:
            return self.create_response(400, error.to_operation_outcome())
        except IdentifierDuplicationError as invalid_error:
            return self.create_response(422, invalid_error.to_operation_outcome())
        except UnhandledResponseError as unhandled_error:
            return self.create_response(500, unhandled_error.to_operation_outcome())

    def update_immunization(self, aws_event):
        imms_id = aws_event["pathParameters"]["id"]
        id_error = self._validate_id(imms_id)
        if id_error:
            return FhirController.create_response(400, json.dumps(id_error))
        try:
            imms = json.loads(aws_event["body"], parse_float=Decimal)
        except json.decoder.JSONDecodeError as e:
            return self._create_bad_request(
                f"Request's body contains malformed JSON: {e}"
            )

        try:
            outcome, resource = self.fhir_service.update_immunization(imms_id, imms)
            if outcome == UpdateOutcome.UPDATE:
                return self.create_response(200)
            elif outcome == UpdateOutcome.CREATE:
                location = f"{get_service_url()}/Immunization/{resource.id}"
                return self.create_response(201, None, {"Location": location})
        except ValidationError as error:
            return self.create_response(400, error.to_operation_outcome())
        except IdentifierDuplicationError as invalid_error:
            return self.create_response(422, invalid_error.to_operation_outcome())

    def delete_immunization(self, aws_event):
        imms_id = aws_event["pathParameters"]["id"]

        id_error = self._validate_id(imms_id)
        if id_error:
            return FhirController.create_response(400, id_error)

        try:
            self.fhir_service.delete_immunization(imms_id)
            return self.create_response(204)
        except ResourceNotFoundError as not_found:
            return self.create_response(404, not_found.to_operation_outcome())
        except UnhandledResponseError as unhandled_error:
            return self.create_response(500, unhandled_error.to_operation_outcome())

    ParamValue = list[str]
    ParamContainer = dict[str, ParamValue]

    nhs_number_key = "-nhsNumber"
    disease_type_key = "-diseaseType"

    @staticmethod
    def process_params(aws_event: APIGatewayProxyEventV1) -> ParamContainer:
        def split_and_flatten(input: list[str]):
            return [x
                    for xs in input
                    for x in xs.split(",")]

        def parse_multi_value_query_parameters(
            multi_value_query_params: dict[str, list[str]]
        ) -> FhirController.ParamContainer:
            params = [(k, split_and_flatten(v))
                      for k, v in multi_value_query_params.items()]

            return dict(params)

        def parse_body_params(aws_event: APIGatewayProxyEventV1) -> FhirController.ParamContainer:
            http_method = aws_event.get("httpMethod")
            content_type = aws_event.get("headers", {}).get("Content-Type")
            if http_method == "POST" and content_type == "application/x-www-form-urlencoded":
                body = aws_event.get("body", "") or ""
                decoded_body = base64.b64decode(body).decode("utf-8")
                parsed_body = parse_qs(decoded_body)

                items = dict((k, split_and_flatten(v)) for k, v in parsed_body.items())
                return items
            return {}

        query_params = parse_multi_value_query_parameters(aws_event.get("multiValueQueryStringParameters", {}))
        body_params = parse_body_params(aws_event)

        return {key: sorted(query_params.get(key, []) + body_params.get(key, []))
                for key in (query_params.keys() | body_params.keys())}

    class SearchParams:
        nhs_number: str
        disease_types: list[str]

        def __init__(self, nhs_number: str, disease_type: list[str]):
            self.nhs_number = nhs_number
            self.disease_types = disease_type

    @staticmethod
    def process_search_params(params: ParamContainer) -> tuple[Optional[SearchParams], Optional[str]]:
        nhs_numbers = params.get(FhirController.nhs_number_key, [])
        nhs_number = nhs_numbers[0] if len(nhs_numbers) == 1 else None

        if nhs_number is None:
            return None, f"Search parameter {FhirController.nhs_number_key} must have one value"

        params[FhirController.disease_type_key] = list(set(params.get(FhirController.disease_type_key, [])))
        disease_types = [disease_type for disease_type in params[FhirController.disease_type_key] if disease_type is not None]
        if len(disease_types) < 1:
            return None, f"Search parameter {FhirController.disease_type_key} must have one or more values"

        return FhirController.SearchParams(nhs_number, disease_types), None

    @staticmethod
    def get_query_string(search_params: SearchParams):
        #params = [(f"-{k}", v) for k, v in search_params.__dict__.items()]
        params = [
            (FhirController.disease_type_key, search_params.disease_types),
            (FhirController.nhs_number_key, search_params.nhs_number)
        ]
        search_params_qs = urllib.parse.urlencode(sorted(params, key=lambda x: x[0]), doseq=True)
        return search_params_qs

    def search_immunizations(self, aws_event: APIGatewayProxyEventV1) -> dict:
        params = self.process_params(aws_event)
        pprint.pprint(params)
        search_params, err = self.process_search_params(params)
        pprint.pprint(search_params)
        if err is not None:
            return self._create_bad_request(err)
        if search_params is None:
            raise Exception("Failed to parse parameters")

        result = self.fhir_service.search_immunizations(
            search_params.nhs_number, search_params.disease_types, self.get_query_string(search_params)
        )
        return self.create_response(200, result.json())

    def _validate_id(self, _id: str) -> Optional[dict]:
        if not re.match(self.immunization_id_pattern, _id):
            msg = (
                "the provided event ID is either missing or not in the expected format."
            )
            return create_operation_outcome(
                resource_id=str(uuid.uuid4()),
                severity=Severity.error,
                code=Code.invalid,
                diagnostics=msg,
            )
        else:
            return None

    def _create_bad_request(self, message):
        error = create_operation_outcome(
            resource_id=str(uuid.uuid4()),
            severity=Severity.error,
            code=Code.invalid,
            diagnostics=message,
        )
        return self.create_response(400, error)

    @staticmethod
    def create_response(status_code, body=None, headers=None):
        if body:
            if isinstance(body, dict):
                body = json.dumps(body)
            if headers:
                headers["Content-Type"] = "application/fhir+json"
            else:
                headers = {"Content-Type": "application/fhir+json"}

        return {
            "statusCode": status_code,
            "headers": headers if headers else {},
            **({"body": body} if body else {}),
        }
