# pylint: disable=invalid-name
# pylint: disable=too-many-ancestors
# pylint: disable=too-many-public-methods
"""
Organizations Data Module Test Cases

Note: 'Unit Test: ' labels are output to the console during test runs
"""
import organizations.data as data
import organizations.tests.utils as utils


class OrganizationsDataTestCase(utils.OrganizationsTestCaseBase):
    """
    Main Test Case module for Organizations Data module
    Many of the module operations are covered indirectly via the test_api.py test suite
    So at the moment we're mainly focused on hitting the corner cases with this suite
    """
    def setUp(self):
        """
        Organizations Data Test Case scaffolding
        """
        super(OrganizationsDataTestCase, self).setUp()

    def test_create_organization(self):
        """ Unit Test: test_create_organization"""
        with self.assertNumQueries(2):
            organization = data.create_organization({
                'name': 'local_organization',
                'short_name': 'organizationX',
                'description': 'Local Organization Description'
            })
        self.assertGreater(organization['id'], 0)
