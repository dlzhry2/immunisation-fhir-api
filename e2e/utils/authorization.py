from enum import Enum
from typing import Set


class ApplicationRestrictedPermission(str, Enum):
    READ = "immunization:read"
    CREATE = "immunization:create"
    UPDATE = "immunization:update"
    DELETE = "immunization:delete"
    SEARCH = "immunization:search"


def make_permissions_attribute(permissions: Set[ApplicationRestrictedPermission]) -> (str, str):
    """it generates an attribute value for application restricted app. It returns key and value"""
    return "Permissions", ",".join(permissions)


def app_res_full_access(exclude: Set[ApplicationRestrictedPermission] = None) -> Set[ApplicationRestrictedPermission]:
    exclude = exclude if exclude else {}
    return {*ApplicationRestrictedPermission}.difference(exclude)
