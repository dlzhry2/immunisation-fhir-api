from validation import validate


def batch_processing_handler(event, context):
    message = f"from batch handler {validate()}"
    print(f"from batch handler {validate()}")
    return {'body': message}
