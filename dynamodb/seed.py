import json

from query import EventTable

SAMPLE_FILE = "sample_data/2023-10-10T18:56:50_10.json"

DYNAMODB_URL = "http://localhost:8000"
TABLE_NAME = "Events3"


def seed(table, sample_file):
    with open(sample_file, "r") as raw_events:
        events = json.loads(raw_events.read())

    for event in events:
        table.put_event(event)

    print(f"{len(events)} events added successfully")


if __name__ == '__main__':
    _table = EventTable(DYNAMODB_URL, TABLE_NAME)
    seed(_table, SAMPLE_FILE)
