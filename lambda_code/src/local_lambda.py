from decimal import Decimal
import json


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f, parse_float=Decimal)

    return json_data


def load_sample_data_json(file_name: str) -> dict:
    return load_json(f"../tests/sample_data/{file_name}")
