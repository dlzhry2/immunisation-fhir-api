import os

env_value = os.environ.get("ENV", "internal-dev")
print(env_value)
INPUT_BUCKET = f"immunisation-batch-{env_value}-data-sources"
INPUT_PREFIX = ""
ACK_BUCKET = "immunisation-batch-internal-dev-data-destinations"
ACK_PREFIX = "forwardedFile/"