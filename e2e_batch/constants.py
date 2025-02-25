import os
from datetime import datetime, timezone

env_value = os.environ.get("ENV", "internal-dev")
print(f"Environment:{env_value}")
SOURCE_BUCKET = f"immunisation-batch-{env_value}-data-sources"
INPUT_PREFIX = ""
ACK_BUCKET = "immunisation-batch-internal-dev-data-destinations"
FORWARDEDFILE_PREFIX = "forwardedFile/"
ACK_PREFIX = "ack/"
PRE_VALIDATION_ERROR = "Validation errors: doseQuantity.value must be a number"
POST_VALIDATION_ERROR = "Validation errors: contained[?(@.resourceType=='Patient')].name[0].given is a mandatory field"
DUPLICATE = "The provided identifier:"

def create_row(unique_id, fore_name, dose_amount, action_flag):
    """Helper function to create a single row with the specified UNIQUE_ID and ACTION_FLAG."""
    return {
        "NHS_NUMBER": "9732928395",
        "PERSON_FORENAME": fore_name,
        "PERSON_SURNAME": "James",
        "PERSON_DOB": "20080217",
        "PERSON_GENDER_CODE": "0",
        "PERSON_POSTCODE": "WD25 0DZ",
        "DATE_AND_TIME": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"),
        "SITE_CODE": "RVVKC",
        "SITE_CODE_TYPE_URI": "https://fhir.nhs.uk/Id/ods-organization-code",
        "UNIQUE_ID": unique_id,
        "UNIQUE_ID_URI": "https://www.ravs.england.nhs.uk/",
        "ACTION_FLAG": action_flag,
        "PERFORMING_PROFESSIONAL_FORENAME": "PHYLIS",
        "PERFORMING_PROFESSIONAL_SURNAME": "James",
        "RECORDED_DATE": datetime.now(timezone.utc).strftime("%Y%m%d"),
        "PRIMARY_SOURCE": "TRUE",
        "VACCINATION_PROCEDURE_CODE": "956951000000104",
        "VACCINATION_PROCEDURE_TERM": "RSV vaccination in pregnancy (procedure)",
        "DOSE_SEQUENCE": "1",
        "VACCINE_PRODUCT_CODE": "42223111000001107",
        "VACCINE_PRODUCT_TERM": "Quadrivalent influenza vaccine (Sanofi Pasteur)",
        "VACCINE_MANUFACTURER": "Sanofi Pasteur",
        "BATCH_NUMBER": "BN92478105653",
        "EXPIRY_DATE": "20240915",
        "SITE_OF_VACCINATION_CODE": "368209003",
        "SITE_OF_VACCINATION_TERM": "Right arm",
        "ROUTE_OF_VACCINATION_CODE": "1210999013",
        "ROUTE_OF_VACCINATION_TERM": "Intradermal use",
        "DOSE_AMOUNT": dose_amount,
        "DOSE_UNIT_CODE": "2622896019",
        "DOSE_UNIT_TERM": "Inhalation - unit of product usage",
        "INDICATION_CODE": "1037351000000105",
        "LOCATION_CODE": "RJC02",
        "LOCATION_CODE_TYPE_URI": "https://fhir.nhs.uk/Id/ods-organization-code",
    }
