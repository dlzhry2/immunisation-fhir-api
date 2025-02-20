import os

env_value = os.environ.get("ENV", "internal-dev")
print(f"Environment:{env_value}")
INPUT_BUCKET = f"immunisation-batch-{env_value}-data-sources"
INPUT_PREFIX = ""
ACK_BUCKET = "immunisation-batch-internal-dev-data-destinations"
FORWARDEDFILE_PREFIX = "forwardedFile/"
ACK_PREFIX = "ack/"
PRE_VALIDATION_ERROR = "Validation errors: doseQuantity.value must be a number"
POST_VALIDATION_ERROR = "Validation errors: contained[?(@.resourceType=='Patient')].name[0].given is a mandatory field"
