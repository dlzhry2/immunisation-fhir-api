import csv
import os
import sys
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")


from models.immunization import ImmunizationModel


def read_csv_to_model(csv_file):
    immunizations = []

    with open(csv_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            try:
                # Filter out unwanted fields
                imms = ImmunizationModel(**row)
                immunizations.append(imms)
            except ValueError as e:
                print(e)

    return immunizations