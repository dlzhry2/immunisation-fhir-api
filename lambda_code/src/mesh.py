from dataclasses import dataclass

import boto3


@dataclass
class MeshImmunisationRecord:
    nhs_number: str
    person_forename: str
    person_surname: str


@dataclass
class MeshImmunisationError:
    message: str


@dataclass
class MeshImmunisationReportEntry:
    error: str


class MeshCsvParser:

    def __init__(self, content):
        self.content = content

    def parse(self) -> ([MeshImmunisationRecord], [MeshImmunisationError]):
        """Parse every CSV record and return a tuple
        first item is a list of successful records and second one is a list of errors
        """
        return ([MeshImmunisationRecord("", "", ""), MeshImmunisationRecord("", "", "")],
                [MeshImmunisationError("error1"), MeshImmunisationError("error2")])


class MeshInputHandler:
    # it's one single Record from the event
    def __init__(self, s3_event_record):
        self.s3_event_record = s3_event_record
        # validation is required for the name of the bundle.
        #  In our case name of the bundle is the csv file name i.e. source object's name
        # TODO: Throw exception if name is not valid.
        #  Exception handler (caller site) should create file.bad in the destination bucket

    def get_event_content(self) -> str:
        bucket = self.s3_event_record["s3"]["bucket"]["name"]
        key = self.s3_event_record["s3"]["object"]["key"]
        client = boto3.client("s3")
        resp = client.get_object(Bucket=bucket, Key=key)

        return resp["Body"].read().decode("utf-8")


class MeshOutputHandler:

    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    def write_report(self, report: [MeshImmunisationReportEntry]):
        client = boto3.client("s3")
        content = MeshOutputHandler.make_report(report)
        resp = client.put_object(Bucket=self.bucket, Key=self.key, Body=content)

        return resp

    # This is a private method. Do not test/mock it. The logic should be tested from the point of caller i.e write_report
    @staticmethod
    def make_report(report: [MeshImmunisationReportEntry]):
        return "the final csv error"


def todo():
    # for each record in the lambda event do:
    #   in = MeshInput(event_record)
    #   content = in.get_source_content() -> str
    #   parse(content) -> (records, validation_errors)
    #   imms_api -> for each record send a request, record api_errors
    #   out = MeshOutput(dest_bucket, key?)
    #   report = out.create_report(validation_errors + api_errors) -> [report_entry] # Are api_errors and validation_errors the same object?
    #   out.write_report(report)
    pass
