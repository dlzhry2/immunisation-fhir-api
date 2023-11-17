import uuid
import datetime
from time import time
import jwt
import requests

ENV = "internal-dev"

with open("jwtRS512-2.key", "r") as f:
    private_key = f.read()

api_key = "URxZoNdcGw36EnSUScAlMwQZgMVZ5HCQ"
kid = "test"

date_file_string = datetime.datetime.now().replace(microsecond=0).isoformat()
log_file_path = "log/log-{0}.log".format(date_file_string)


def log(text):
    with open(log_file_path, "a") as log_file:
        print(f"{datetime.datetime.now()} - {text}", file=log_file)
    print(f"{datetime.datetime.now()} - {text}")


def get_access_token():
    claims = {
        "sub": api_key,
        "iss": api_key,
        "jti": str(uuid.uuid4()),
        "aud": f"https://{ENV}.api.service.nhs.uk/oauth2/token",
        "exp": int(time()) + 300,  # 5 mins in the future
    }

    additional_headers = {"kid": {kid}}

    j = str(jwt.encode(claims, private_key, algorithm="RS512", headers=additional_headers))
    token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    token_response = requests.post(f"https://{ENV}.api.service.nhs.uk/oauth2/token", 'grant_type=client_credentials\
&client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer\
&client_assertion=' + j, headers=token_headers)

    print(token_response.json())
    return token_response.json()['access_token']


access_token = get_access_token()
print(access_token)