from validation import validate


def get_status_handler(event, context):
    message = f"from status handler {validate()}"
    return {'body': message}
