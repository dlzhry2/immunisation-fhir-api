import json
import os
from typing import Optional
import boto3


class FhirRepository:
    def __init__(self, table_name=None, endpoint_url=None):
        if not table_name:
            table_name = os.environ["DYNAMODB_TABLE_NAME"]
        db = boto3.resource("dynamodb", endpoint_url=endpoint_url, region_name='eu-west-2')
        self.table = db.Table(table_name)


class ImmunisationRepository(FhirRepository):
    def get_immunisation_by_id(self, imms_id: str) -> Optional[dict]:
        response = self.table.get_item(Key={"PK": imms_id})

        if "Item" in response:
            return json.loads(response["Item"]["Event"])
        else:
            return None
