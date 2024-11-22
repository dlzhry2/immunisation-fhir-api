import os
import uuid
import boto3
import time
import simplejson as json
from dataclasses import dataclass
import botocore.exceptions
from boto3.dynamodb.conditions import Key, Attr
from models.errors import (
    UnhandledResponseError,
    IdentifierDuplicationError,
    ResourceNotFoundError,
)


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
        query_response = _query_identifier(
            table, "IdentifierGSI", "IdentifierPK", self._identifier_response(immunization)
        )
        print(f"query_response: {query_response}")

    def delete_immunization(
        self, immunization: any, supplier_system: str, vax_type: str, table: any
    ) -> dict:
        identifier = self._identifier_response(immunization)
        query_response = _query_identifier(
            table, "IdentifierGSI", "IdentifierPK", identifier
        )
        if query_response is None:
            raise ResourceNotFoundError(
                    resource_type="Immunization", resource_id=identifier
                )
        try:
            now_timestamp = int(time.time())
            imms_id = self._get_pk(query_response)
            response = table.update_item(
                Key={"PK": imms_id },
                UpdateExpression="SET DeletedAt = :timestamp, Operation = :operation, SupplierSystem = :supplier_system",
                ExpressionAttributeValues={
                    ":timestamp": now_timestamp,
                    ":operation": "DELETE",
                    ":supplier_system": supplier_system,
                },
                ReturnValues="ALL_NEW",
                ConditionExpression=Attr("PK").eq(imms_id)
                & (Attr("DeletedAt").not_exists() | Attr("DeletedAt").eq("reinstated")),
            )
            return self._handle_dynamo_response(response)

        except botocore.exceptions.ClientError as error:
            # Either resource didn't exist or it has already been deleted. See ConditionExpression in the request
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ResourceNotFoundError(
                    resource_type="Immunization", resource_id=imms_id
                )
            else:
                raise UnhandledResponseError(
                    message=f"Unhandled error from dynamodb: {error.response['Error']['Code']}",
                    response=error.response,
                )

    @staticmethod
    def _handle_dynamo_response(response):
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return json.loads(response["Attributes"]["Resource"])
        else:
            raise UnhandledResponseError(
                message="Non-200 response from dynamodb", response=response
            )
            
    @staticmethod
    def _identifier_response(immunization: any):
        system_id = immunization["identifier"][0]["system"]
        system_value = immunization["identifier"][0]["value"]

        return f"{system_id}#{system_value}"
    
    @staticmethod
    def _get_pk(immunization: any):
        if immunization.get("Count") == 1:
            return immunization["Items"][0]["PK"]
