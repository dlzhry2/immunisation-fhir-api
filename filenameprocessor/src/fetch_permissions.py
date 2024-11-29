import json
from clients import redis_client


FILE_KEY = "permissions_config.json"


def get_permissions_config_json_from_cache():
    """Gets the permissions config file content from ElastiCache."""
    return json.loads(redis_client.get(FILE_KEY))
