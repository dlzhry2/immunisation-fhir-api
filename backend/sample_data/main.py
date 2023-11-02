import csv
import os
import sys
import json

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")

from pyutils.csv_to_model import read_csv_to_model
from pyutils.model_to_fhir import convert_to_fhir
# THIS main file is temporary, jsut to see if things are working as expected




if __name__ == "__main__":
    csv_file = "patient_data.csv"
    immunizations = read_csv_to_model(csv_file)

    for imms in immunizations:
        print(imms)
        print("********************************+++++++++++++++++++++===============================")
        fhir_imms = convert_to_fhir(imms)
        expected_json = json.loads(fhir_imms.get_bundle())
        print(json.dumps(expected_json, indent=2))

