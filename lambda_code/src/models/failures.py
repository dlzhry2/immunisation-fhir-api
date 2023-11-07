from pydantic import BaseModel


class CsvImmunizationErrorModel(BaseModel):
    nhs_number: str = None
    unique_id: str = None
    failure_reasons: list = None
