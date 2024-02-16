import logging
import os
import subprocess


def apigee_access_token(username: str = None):
    if access_token := os.getenv("APIGEE_ACCESS_TOKEN"):
        return access_token
    if username := username or os.getenv("APIGEE_USERNAME"):
        env = os.environ.copy()
        env["SSO_LOGIN_URL"] = env.get("SSO_LOGIN_URL", "https://login.apigee.com")
        try:
            res = subprocess.run(["get_token", "-u", username], env=env, stdout=subprocess.PIPE, text=True)
            return res.stdout.strip()
        except FileNotFoundError:
            logging.error("Make sure you install apigee's get_token utility and it's in your PATH. "
                          "Follow: https://docs.apigee.com/api-platform/system-administration/using-gettoken")


if __name__ == '__main__':
    a = apigee_access_token("jalal.hosseini1@nhs.net")
    print(a)
