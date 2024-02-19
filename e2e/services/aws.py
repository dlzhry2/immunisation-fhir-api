"""All functions in this module uses your system AWS CLI. It runs the cli in a process.
NOTE: if you get errors just try to run the command that this module is running using the same terminal.
"""


class AwsService:
    def __init__(self, public_bucket: str):
        self.pub_bucket = public_bucket
