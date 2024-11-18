import os
import uuid
import boto3
from dataclasses import dataclass
from boto3.dynamodb.conditions import Key
from botocore.config import Config
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from models.errors import UnhandledResponseError, IdentifierDuplicationError


def create_table(table_name=None, endpoint_url=None, region_name="eu-west-2"):
    if not table_name:
        table_name = os.environ["DYNAMODB_TABLE_NAME"]
    config = Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 1})
    db: DynamoDBServiceResource = boto3.resource(
        "dynamodb", endpoint_url=endpoint_url, region_name=region_name, config=config
    )
    return db.Table(table_name)


def _make_immunization_pk(_id: str):
    return f"Immunization#{_id}"


def _make_patient_pk(_id: str):
    return f"Patient#{_id}"


def _query_identifier(table, index, pk, identifier):
    queryresponse = table.query(
        IndexName=index, KeyConditionExpression=Key(pk).eq(identifier), Limit=1
    )
    if queryresponse.get("Count", 0) > 0:
        return queryresponse


def get_nhs_number(imms):
    try:
        nhs_number = [x for x in imms["contained"] if x["resourceType"] == "Patient"][
            0
        ]["identifier"][0]["value"]
    except (KeyError, IndexError):
        nhs_number = "TBC"
    return nhs_number


@dataclass
class RecordAttributes:
    pk: str
    patient_pk: str
    patient_sk: str
    resource: dict
    vaccine_type: str
    nhs_number: str
    identifier: str

    def __init__(self, immunization: any, vax_type: str):
        """Create attributes that may be used in dynamodb table"""
        imms_id = immunization["id"]
        self.pk = _make_immunization_pk(imms_id)
        nhs_number = get_nhs_number(immunization)
        self.patient_pk = _make_patient_pk(nhs_number)
        self.resource = immunization
        self.vaccine_type = vax_type
        self.system_id = immunization["identifier"][0]["system"]
        self.system_value = immunization["identifier"][0]["value"]
        self.patient_sk = f"{self.vaccine_type}#{imms_id}"
        self.identifier = f"{self.system_id}#{self.system_value}"


class ImmunizationRepository:
    def __init__(self, table: Table):
        self.table = table

    def create_immunization(
        self, immunization: any, supplier_system: str, vax_type: str
    ) -> dict:
        new_id = str(uuid.uuid4())
        immunization["id"] = new_id
        attr = RecordAttributes(immunization, vax_type)

        query_response = _query_identifier(
            self.table, "IdentifierGSI", "IdentifierPK", attr.identifier
        )

        if query_response is not None:
            raise IdentifierDuplicationError(identifier=attr.identifier)

        response = self.table.put_item(
            Item={
                "PK": attr.pk,
                "PatientPK": attr.patient_pk,
                "PatientSK": attr.patient_sk,
                "Resource": immunization,
                "IdentifierPK": attr.identifier,
                "Operation": "CREATE",
                "Version": 1,
                "SupplierSystem": supplier_system,
            }
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return immunization
        else:
            raise UnhandledResponseError(
                message="Non-200 response from dynamodb", response=response
            )
