import json

from query import EventTable

sample_file = "sample_data/2023-11-09T19:09:23_immunisation-30.json"

dynamodb_url = "http://localhost:4566"
table_name = "local-imms-events"


def seed_immunisation(table, sample_file):
    with open(sample_file, "r") as raw_data:
        imms_list = json.loads(raw_data.read())

    for imms in imms_list:
        table.create_immunisation(imms)

    print(f"{len(imms_list)} events added successfully")


if __name__ == '__main__':
    _table = EventTable(dynamodb_url, table_name)
    seed_immunisation(_table, sample_file)
