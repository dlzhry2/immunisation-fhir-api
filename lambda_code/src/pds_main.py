#!/Users/ewan.childs/Desktop/NHS/Bebop/immunisation-fhir-api/.venv/bin/python3.9
from pds_controller import PdsController

def main():
    pds_controller = PdsController()
    patient_id = 9693632109  # Replace this with a valid patient ID
    response = pds_controller.get_patient_details(patient_id)
    
    if response.status_code == 200:
        print("Patient details retrieved successfully:")
        print(response.json())
    else:
        print("Failed to retrieve patient details.")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

if __name__ == "__main__":
    main()
