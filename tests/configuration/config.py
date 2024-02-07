from .environment import ENV

# Api Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"
BASE_PATH = ENV["base_path"]

valid_nhs_number1 = "9693632109"
valid_nhs_number2 = "9693633687"
valid_nhs_number_with_s_flag = "9449310610"
