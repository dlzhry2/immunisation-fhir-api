import base64
import datetime
from aws_lambda_typing.events import APIGatewayProxyEventV1
from typing import Optional
from urllib.parse import parse_qs, urlencode

from mappings import VaccineTypes

ParamValue = list[str]
ParamContainer = dict[str, ParamValue]

patient_identifier_system = "https://fhir.nhs.uk/Id/nhs-number"

patient_identifier_key = "patient.identifier"
immunization_target_key = "-immunization.target"
date_from_key = "-date.from"
date_to_key = "-date.to"


class SearchParams:
    nhs_number: str
    disease_types: list[str]
    date_from: Optional[datetime.date]
    date_to: Optional[datetime.date]

    def __init__(self,
                 nhs_number: str,
                 disease_type: list[str],
                 date_from: Optional[datetime.date],
                 date_to: Optional[datetime.date]):
        self.nhs_number = nhs_number
        self.disease_types = disease_type
        self.date_from = date_from
        self.date_to = date_to

    def __repr__(self):
        return str(self.__dict__)


def process_params(aws_event: APIGatewayProxyEventV1) -> ParamContainer:
    def split_and_flatten(input: list[str]):
        return [x.strip()
                for xs in input
                for x in xs.split(",")]

    def parse_multi_value_query_parameters(
        multi_value_query_params: dict[str, list[str]]
    ) -> ParamContainer:
        if any([isinstance(v, list) is False for _, v in multi_value_query_params.items()]):
            raise Exception("Parameter values must be lists.")
        if any([len(v) > 1 for k, v in multi_value_query_params.items()]):
            raise Exception("Parameters may not be duplicated. Use commas for \"or\".")
        params = [(k, split_and_flatten(v))
                  for k, v in multi_value_query_params.items()]

        return dict(params)

    def parse_body_params(aws_event: APIGatewayProxyEventV1) -> ParamContainer:
        http_method = aws_event.get("httpMethod")
        content_type = aws_event.get("headers", {}).get("Content-Type")
        if http_method == "POST" and content_type == "application/x-www-form-urlencoded":
            body = aws_event.get("body", "") or ""
            decoded_body = base64.b64decode(body).decode("utf-8")
            parsed_body = parse_qs(decoded_body)

            if any([isinstance(v, list) is False for _, v in parsed_body.items()]):
                raise Exception("Parameter values must be lists.")
            if any([len(v) > 1 for k, v in parsed_body.items()]):
                raise Exception("Parameters may not be duplicated. Use commas for \"or\".")
            items = dict((k, split_and_flatten(v)) for k, v in parsed_body.items())
            return items
        return {}

    query_params = parse_multi_value_query_parameters(aws_event.get("multiValueQueryStringParameters", {}) or {})
    body_params = parse_body_params(aws_event)

    return {key: sorted(query_params.get(key, []) + body_params.get(key, []))
            for key in (query_params.keys() | body_params.keys())}


def process_search_params(params: ParamContainer) -> tuple[Optional[SearchParams], Optional[str]]:
    # patient.identifier
    patient_identifiers = params.get(patient_identifier_key, [])
    patient_identifier = patient_identifiers[0] if len(patient_identifiers) == 1 else None

    if patient_identifier is None:
        return None, f"Search parameter {patient_identifier_key} must have one value."

    patient_identifier_parts = patient_identifier.split("|")
    if len(patient_identifier_parts) != 2 or not patient_identifier_parts[
                                                     0] == patient_identifier_system:
        return None, ("patient.identifier must be in the format of "
                      f"\"{patient_identifier_system}|{{NHS number}}\" "
                      f"e.g. \"{patient_identifier_system}|9000000009\"")

    patient_identifier = patient_identifier.split("|")[1]

    # immunization.target
    params[immunization_target_key] = list(set(params.get(immunization_target_key, [])))
    disease_types = [disease_type for disease_type in params[immunization_target_key] if
                     disease_type is not None]
    if len(disease_types) < 1:
        return None, f"Search parameter {immunization_target_key} must have one or more values."
    if any([x not in VaccineTypes().all for x in disease_types]):
        return None, f"immunization-target must be one or more of the following: {','.join(VaccineTypes().all)}"

    # date.from
    date_froms = params.get(date_from_key, [])

    if len(date_froms) > 1:
        return None, f"Search parameter {date_from_key} may have only one value."

    try:
        date_from = datetime.datetime.strptime(date_froms[0], "%Y-%m-%d").date() \
            if len(date_froms) == 1 else datetime.date(1900, 1, 1)
    except ValueError:
        return None, f"Search parameter {date_from_key} must be in format: YYYY-MM-DD"

    # date.to
    date_tos = params.get(date_to_key, [])

    if len(date_tos) > 1:
        return None, f"Search parameter {date_to_key} may have only one value."

    try:
        date_to = datetime.datetime.strptime(date_tos[0], "%Y-%m-%d").date() \
            if len(date_tos) == 1 else datetime.date(9999, 12, 31)
    except ValueError:
        return None, f"Search parameter {date_to_key} must be in format: YYYY-MM-DD"

    if date_from and date_to and date_from > date_to:
        return None, f"Search parameter {date_from_key} must be before {date_to_key}"

    return SearchParams(patient_identifier, disease_types, date_from, date_to), None

def create_query_string(search_params: SearchParams):
    params = [
        (immunization_target_key, search_params.disease_types),
        (patient_identifier_key,
         f"{patient_identifier_system}|{search_params.nhs_number}")
    ]
    search_params_qs = urlencode(sorted(params, key=lambda x: x[0]), doseq=True)
    return search_params_qs
