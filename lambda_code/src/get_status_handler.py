def get_status_handler(event, context):
    status_response = {"status": "healthy", "message": "Backend is up and running."}
    return status_response
