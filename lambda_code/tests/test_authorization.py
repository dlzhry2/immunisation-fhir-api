import unittest
from typing import Set

from authorization_service import ImmunizationPermission as Perm, parse_permissions, ApplicationRestrictedAuthorization, \
    PERMISSIONS_HEADER, UnknownPermission, EndpointOperation as Operation
from models.errors import Unauthorized


def _make_aws_event(permissions: Set[str]):
    header = ",".join(permissions)
    return {
        "headers": {
            PERMISSIONS_HEADER: header
        }
    }


def _full_access(exclude: Set[Perm] = None):
    return {*Perm}.difference(exclude)


class TestPermission(unittest.TestCase):
    def test_parse_permissions(self):
        """it should create a set of permissions from request's headers"""
        # test for case-insensitive, trim and duplicated
        permissions = {"immunization:create\n", "\timmunization:update ", "Immunization:UPDATE "}
        aws_event = _make_aws_event(permissions)

        # When
        header = parse_permissions(aws_event["headers"])

        # Then
        exp_permissions = {Perm.CREATE, Perm.UPDATE}
        self.assertSetEqual(header, exp_permissions)

    def test_unknown_permission(self):
        permissions = {"immunization:create", "bad-permission"}
        aws_event = _make_aws_event(permissions)

        with self.assertRaises(UnknownPermission):
            # When
            parse_permissions(aws_event["headers"])


class TestApplicationRestrictedAuthorization(unittest.TestCase):
    def setUp(self):
        self.authorization = ApplicationRestrictedAuthorization()

    def test_get_endpoint(self):
        """it should allow GET only if application has READ access"""
        # Authorized
        event = _make_aws_event({Perm.READ})
        try:
            self.authorization.authorize(Operation.READ, event)
        except Unauthorized:
            self.fail()

        # Unauthorized
        event = _make_aws_event(_full_access(exclude={Perm.READ}))
        with self.assertRaises(Unauthorized):
            self.authorization.authorize(Operation.READ, event)
