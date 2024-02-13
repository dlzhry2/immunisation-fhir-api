from dataclasses import dataclass
from enum import Enum
from typing import Set

from models.errors import Unauthorized

PERMISSIONS_HEADER = "Permissions"


@dataclass
class UnknownPermission(RuntimeError):
    """Error when the parsed value can't be converted to Permissions enum."""


class ImmunizationPermission(str, Enum):
    READ = "immunization:read"
    CREATE = "immunization:create"
    UPDATE = "immunization:update"
    DELETE = "immunization:delete"
    SEARCH = "immunization:search"


def parse_permissions(headers) -> Set[ImmunizationPermission]:
    """Given headers return a set of ImmunizationPermissions. Raises UnknownPermission"""

    content = headers.get("Permissions", "")
    # comma separate the Permissions header then trim and finally convert to lower case
    parsed = [str.strip(str.lower(s)) for s in content.split(",")]

    permissions = set()
    for s in parsed:
        try:
            permissions.add(ImmunizationPermission(s))
        except ValueError:
            raise UnknownPermission()

    return permissions


class EndpointOperation(Enum):
    """The kind of operation.
    This maps one-to-one to each endpoint. Authorization service decides whether there is sufficient permissions or not.
    The caller is responsible for passing the correct operation.
    """
    READ = 0,
    CREATE = 1,
    UPDATE = 2,
    DELETE = 3,
    SEARCH = 4,


class ApplicationRestrictedAuthorization:
    _permission_map = {
        EndpointOperation.READ: {ImmunizationPermission.READ},
        EndpointOperation.CREATE: {ImmunizationPermission.CREATE},
        EndpointOperation.UPDATE: {ImmunizationPermission.UPDATE, ImmunizationPermission.CREATE},
        EndpointOperation.DELETE: {ImmunizationPermission.DELETE},
        EndpointOperation.SEARCH: {ImmunizationPermission.SEARCH},
    }

    def authorize(self, operation: EndpointOperation, aws_event: dict) -> None:
        allowed = parse_permissions(aws_event["headers"])
        requested = self._permission_map[operation]
        if not requested.issubset(allowed):
            raise Unauthorized()
