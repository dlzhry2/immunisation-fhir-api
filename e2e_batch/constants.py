import os

env_value = os.environ.get("ENV", "internal-dev")
INPUT_BUCKET = f"immunisation-batch-{env_value}-data-sources"
INPUT_PREFIX = ""
ACK_BUCKET = "immunisation-batch-internal-dev-data-destinations"
FORWARDEDFILE_PREFIX = "forwardedFile/"
ACK_PREFIX = "ack/"
