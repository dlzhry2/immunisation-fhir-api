from fhir.resources.quantity import Quantity as FHIRQuantity


def validate():
    return f"{FHIRQuantity()} validate"


if __name__ == '__main__':
    print(validate())

# dfdsf
