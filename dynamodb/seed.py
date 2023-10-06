import json

from query import EventTable

SAMPLE_FILE = "sample_data/2023-10-06T15:41:11_10.json"

DYNAMODB_URL = "http://localhost:8000"
TABLE_NAME = "imms-events"


def seed(table, sample_file):
    with open(sample_file, "r") as raw_events:
        events = json.loads(raw_events.read())

    for event in events:
        table.put_event(event)

    print(f"{len(events)} events added successfully")


if __name__ == '__main__':
    _table = EventTable(DYNAMODB_URL, TABLE_NAME)
    seed(_table, SAMPLE_FILE)
