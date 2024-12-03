import json
import logging
from clients import redis_client

logger = logging.getLogger()

FILE_KEY = "permissions_config.json"


def get_permissions_config_json_from_cache():
    """Gets the permissions config file content from ElastiCache."""
    return json.loads(redis_client.get(FILE_KEY))


def get_supplier_permissions(supplier: str) -> list:
    """
    Returns the permissions for the given supplier. Returns an empty list if the permissions config json could not
    be downloaded, or the supplier has no permissions.
    """
    permissions_config = get_permissions_config_json_from_cache()
    return permissions_config.get("all_permissions", {}).get(supplier, [])


def validate_vaccine_type_permissions(supplier: str, vaccine_type: str) -> bool:
    """Returns True if the given supplier has any permissions for the given vaccine type, else False"""
    supplier_permissions = get_supplier_permissions(supplier)

    # Validate has permissions for the vaccine type
    if not any(vaccine_type in permission for permission in supplier_permissions):
        logger.error("Initial file validation failed: %s does not have permissions for %s", supplier, vaccine_type)
        raise Exception(f"Initial file validation failed: {supplier} does not have permissions for {vaccine_type}")

    return supplier_permissions
