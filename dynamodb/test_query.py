import json

from dynamodb.generate_data import PATIENT_POOL, DISEASE_TYPE
from dynamodb.query import EventTable

DYNAMODB_URL = "http://localhost:8000"
TABLE_NAME = "Imms"
TABLE = EventTable(DYNAMODB_URL, TABLE_NAME)


class TestQuery:
    @staticmethod
    def test_query_event_id():
        with open("sample_event.json", "r") as event_file:
            act_event = json.loads(event_file.read())
        event_id = act_event["identifier"][0]["value"]

        response = TABLE.put_event(act_event)
        assert response == act_event

        persisted_event = TABLE.get_event_by_id(event_id)
        assert persisted_event["identifier"][0]["value"] == event_id

        response = TABLE.delete_event(event_id)
        assert response == event_id

    @staticmethod
    def test_get_by_nhs_number():
        nhs_num = PATIENT_POOL[0]["nhs_number"]

        events = TABLE.get_patient(nhs_num)

        assert len(events) > 0
        for event in events:
            patient = json.loads(event["Event"])["patient"]
            assert nhs_num == patient["identifier"][0]["value"]

    @staticmethod
    def test_get_by_nhs_number_and_dob():
        nhs_num = PATIENT_POOL[0]["nhs_number"]
        dob = PATIENT_POOL[0]["dob"]

        events = TABLE.get_patient(nhs_num, {"dateOfBirth": dob})

        assert len(events) > 0
        for event in events:
            patient = json.loads(event["Event"])["patient"]
            assert nhs_num == patient["identifier"][0]["value"]
            assert dob == patient["birthDate"]

        events = TABLE.get_patient(nhs_num, {"dateOfBirth": '1904-01-01'})
        assert len(events) == 0

    @staticmethod
    def test_get_by_nhs_number_dob_and_disease_type():
        nhs_num = PATIENT_POOL[0]["nhs_number"]
        dob = PATIENT_POOL[0]["dob"]
        disease = DISEASE_TYPE[0]

        events = TABLE.get_patient(nhs_num, {"dateOfBirth": dob, "diseaseType": disease})

        assert len(events) > 0
        for event in events:
            event = json.loads(event["Event"])
            patient = event["patient"]
            assert nhs_num == patient["identifier"][0]["value"]
            assert dob == patient["birthDate"]
            assert disease == event["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"]

        events = TABLE.get_patient(nhs_num, {"dateOfBirth": dob, "diseaseType": "doesnt_exists"})
        assert len(events) == 0
