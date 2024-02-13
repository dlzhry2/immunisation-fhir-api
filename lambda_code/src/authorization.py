from dataclasses import dataclass
from enum import Enum
from typing import Set

from models.errors import Unauthorized

PERMISSIONS_HEADER = "Permissions"
AUTHENTICATION_HEADER = "AuthenticationType"


@dataclass
class UnknownPermission(RuntimeError):
    """Error when the parsed value can't be converted to Permissions enum."""


class EndpointOperation(Enum):
    """The kind of operation.
    This maps one-to-one to each endpoint. Authorization class decides whether there is sufficient permissions or not.
    The caller is responsible for passing the correct operation.
    """
    READ = 0,
    CREATE = 1,
    UPDATE = 2,
    DELETE = 3,
    SEARCH = 4,


class Authorization:
    """ Authorize the call based on the endpoint and the authentication type.
    This class uses the passed headers from Apigee to decide the type of authentication (Application Restricted,
    NHS Login or CIS2). Then, based on the requested operation, it authorizes the call. Unauthorized call will raise
    Unauthorized exception. It raises UnknownPermission if there is a parse error.
    """

    def authorize(self, operation: EndpointOperation, aws_event: dict):
        self._app_restricted(operation, aws_event)

    class _AuthType(str, Enum):
        APP_RESTRICTED = "ApplicationRestricted",
        NHS_LOGIN = "NnsLogin",
        CIS2 = "Cis2",

    class _Permission(str, Enum):
        READ = "immunization:read"
        CREATE = "immunization:create"
        UPDATE = "immunization:update"
        DELETE = "immunization:delete"
        SEARCH = "immunization:search"

    _app_restricted_map = {
        EndpointOperation.READ: {_Permission.READ},
        EndpointOperation.CREATE: {_Permission.CREATE},
        EndpointOperation.UPDATE: {_Permission.UPDATE, _Permission.CREATE},
        EndpointOperation.DELETE: {_Permission.DELETE},
        EndpointOperation.SEARCH: {_Permission.SEARCH},
    }

    def _app_restricted(self, operation: EndpointOperation, aws_event: dict) -> None:
        allowed = self._parse_permissions(aws_event["headers"])
        requested = self._app_restricted_map[operation]
        if not requested.issubset(allowed):
            raise Unauthorized()

    @staticmethod
    def _parse_permissions(headers) -> Set[_Permission]:
        """Given headers return a set of ImmunizationPermissions. Raises UnknownPermission"""

        content = headers.get(PERMISSIONS_HEADER, "")
        # comma separate the Permissions header then trim and finally convert to lower case
        parsed = [str.strip(str.lower(s)) for s in content.split(",")]

        permissions = set()
        for s in parsed:
            try:
                permissions.add(Authorization._Permission(s))
            except ValueError:
                raise UnknownPermission()

        return permissions
