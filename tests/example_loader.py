import json
import os
from decimal import Decimal

current_directory = os.path.dirname(os.path.realpath(__file__))


def load_example(path: str):
    with open(f"{current_directory}/../specification/components/examples/{path}") as f:
        if path.endswith("json"):
            return json.load(f, parse_float=Decimal)
        else:
            return f.read().strip()
