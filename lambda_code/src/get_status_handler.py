def get_status_handler(event, context):
    response = {
        "statusCode": 200,  # HTTP status code
        "body": "Backend is up and running"
    }
    return response
