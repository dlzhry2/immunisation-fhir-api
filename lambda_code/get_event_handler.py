from validation import validate


def get_event_handler(event, context):
    message = f"from get event handler {validate()}"
    return {'body': message}
