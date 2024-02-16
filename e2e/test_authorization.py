import unittest

from services.apigee import ApigeeService, ApigeeConfig, ApigeeOrg


class TestAuthorization(unittest.TestCase):
    def setUp(self):
        config = ApigeeConfig(org=ApigeeOrg.NON_PROD)
        self.apigee = ApigeeService(config)

    def test_foo(self):
        # l = self.apigee.get_applications()
        # app = self.apigee.create_application(ApigeeApp(name="jalal-test123"))
        app = self.apigee.delete_application(name="jalal-test123")
        print(app)
        self.assertTrue(True)
