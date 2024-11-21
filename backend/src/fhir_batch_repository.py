import os
import uuid
import boto3
import time
import simplejson as json
from dataclasses import dataclass
from boto3.dynamodb.conditions import Key
from models.errors import UnhandledResponseError, IdentifierDuplicationError


def create_table(region_name="eu-west-2"):
    table_name = os.environ["DYNAMODB_TABLE_NAME"]
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    return dynamodb.Table(table_name)


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
    patient: dict
    vaccine_type: str
    timestamp: int
    identifier: str

    def __init__(self, imms: dict, vax_type: str):
        """Create attributes that may be used in dynamodb table"""
        imms_id = imms["id"]
        self.pk = _make_immunization_pk(imms_id)
        nhs_number = get_nhs_number(imms)
        self.patient_pk = _make_patient_pk(nhs_number)
        self.resource = imms
        self.timestamp = int(time.time())
        self.vaccine_type = vax_type
        self.system_id = imms["identifier"][0]["system"]
        self.system_value = imms["identifier"][0]["value"]
        self.patient_sk = f"{self.vaccine_type}#{imms_id}"
        self.identifier = f"{self.system_id}#{self.system_value}"


class ImmunizationBatchRepository:
    def __init__(self):
        pass

    def create_immunization(
        self, immunization: any, supplier_system: str, vax_type: str, table: any
    ) -> dict:
        new_id = str(uuid.uuid4())
        immunization["id"] = new_id
        attr = RecordAttributes(immunization, vax_type)

        query_response = _query_identifier(
            table, "IdentifierGSI", "IdentifierPK", attr.identifier
        )

        if query_response is not None:
            raise IdentifierDuplicationError(identifier=attr.identifier)

        response = table.put_item(
            Item={
                "PK": attr.pk,
                "PatientPK": attr.patient_pk,
                "PatientSK": attr.patient_sk,
                "Resource": json.dumps(attr.resource, use_decimal=True),
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

    def update_immunization(
        self, immunization: any, supplier_system: str, vax_type: str, table: any
    ) -> dict:
        new_id = str(uuid.uuid4())
        immunization["id"] = new_id
        attr = RecordAttributes(immunization, vax_type)

        query_response = _query_identifier(
            table, "IdentifierGSI", "IdentifierPK", attr["identifier"]
        )

        if query_response is not None:
            raise IdentifierDuplicationError(identifier=attr["identifier"])

        response = table.put_item(
            Item={
                "PK": attr["pk"],
                "PatientPK": attr["patient_pk"],
                "PatientSK": attr["patient_sk"],
                "Resource": immunization,
                "IdentifierPK": attr["identifier"],
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

    def delete_immunization(
        self, immunization: any, supplier_system: str, vax_type: str, table: any
    ) -> dict:
        new_id = str(uuid.uuid4())
        immunization["id"] = new_id
        attr = RecordAttributes(immunization, vax_type)

        query_response = _query_identifier(
            table, "IdentifierGSI", "IdentifierPK", attr["identifier"]
        )

        if query_response is not None:
            raise IdentifierDuplicationError(identifier=attr["identifier"])

        response = table.put_item(
            Item={
                "PK": attr["pk"],
                "PatientPK": attr["patient_pk"],
                "PatientSK": attr["patient_sk"],
                "Resource": immunization,
                "IdentifierPK": attr["identifier"],
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
