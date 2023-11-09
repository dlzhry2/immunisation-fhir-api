import json
import unittest

from generate_data import patient_pool, disease_type
from query import EventTable


class TestRepository(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        _dynamodb_url = "http://localhost:4566"
        _table_name = "local-imms-events"
        self.table = EventTable(_dynamodb_url, _table_name)

    def test_crud_immunisation(self):
        with open("sample_imms.json", "r") as imms_file:
            act_imms = json.loads(imms_file.read())
        imms_id = act_imms["id"]

        response = table.create_immunisation(act_imms)
        assert response == act_imms

        persisted_imms = table.get_immunisation_by_id(imms_id)
        assert persisted_imms["id"] == imms_id

        response = table.delete_immunisation(imms_id)
        assert response == imms_id

    def test_delete_should_be_logical(self):
        with open("sample_imms.json", "r") as imms_file:
            an_imms = json.loads(imms_file.read())

        imms_id = "delete-me"
        an_imms["id"] = imms_id
        table.create_immunisation(an_imms)

        response = table.delete_immunisation(imms_id)
        assert response == imms_id

    def test_multiple_delete_should_not_update_timestamp(self):
        pass

    def test_imms_by_id_should_return_none_if_it_is_deleted(self):
        imms_id = "delete-me"
        res = table.get_immunisation_by_id(imms_id)
        self.assertIsNone(res)


dynamodb_url = "http://localhost:4566"
table_name = "local-imms-events"

table = EventTable(dynamodb_url, table_name)


# Deprecated: Move test to the above class. Use unittest
class TestQuery:
    @staticmethod
    def test_query_event_id():
        with open("sample_event.json", "r") as event_file:
            act_event = json.loads(event_file.read())
        event_id = act_event["identifier"][0]["value"]

        response = table.put_event(act_event)
        assert response == act_event

        persisted_event = table.get_event_by_id(event_id)
        assert persisted_event["identifier"][0]["value"] == event_id

        response = table.delete_event(event_id)
        assert response == event_id

    @staticmethod
    def test_get_by_nhs_number():
        nhs_num = patient_pool[0]["nhs_number"]

        events = table.get_patient(nhs_num)

        assert len(events) > 0
        for event in events:
            patient = json.loads(event["Event"])["patient"]
            assert nhs_num == patient["identifier"][0]["value"]

    @staticmethod
    def test_get_by_nhs_number_and_dob():
        nhs_num = patient_pool[0]["nhs_number"]
        dob = patient_pool[0]["dob"]

        events = table.get_patient(nhs_num, {"dateOfBirth": dob})

        assert len(events) > 0
        for event in events:
            patient = json.loads(event["Event"])["patient"]
            assert nhs_num == patient["identifier"][0]["value"]
            assert dob == patient["birthDate"]

        events = table.get_patient(nhs_num, {"dateOfBirth": '1904-01-01'})
        assert len(events) == 0

    @staticmethod
    def test_get_by_nhs_number_dob_and_disease_type():
        nhs_num = patient_pool[0]["nhs_number"]
        dob = patient_pool[0]["dob"]
        disease = disease_type[0]

        events = table.get_patient(nhs_num, {"dateOfBirth": dob, "diseaseType": disease})

        assert len(events) > 0
        for event in events:
            event = json.loads(event["Event"])
            patient = event["patient"]
            assert nhs_num == patient["identifier"][0]["value"]
            assert dob == patient["birthDate"]
            assert disease == event["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"]

        events = table.get_patient(nhs_num, {"dateOfBirth": dob, "diseaseType": "doesnt_exists"})
        assert len(events) == 0
