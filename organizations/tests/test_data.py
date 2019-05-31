"""
Organizations Data Module Test Cases

Note: 'Unit Test: ' labels are output to the console during test runs
"""
import organizations.data as data
import organizations.tests.utils as utils

from organizations.tests.factories import OrganizationFactory


class OrganizationsDataTestCase(utils.OrganizationsTestCaseBase):
    """
    Main Test Case module for Organizations Data module
    Many of the module operations are covered indirectly via the test_api.py test suite
    So at the moment we're mainly focused on hitting the corner cases with this suite
    """
    def test_create_organization(self):
        """ Unit Test: test_create_organization"""
        with self.assertNumQueries(3):
            organization = data.create_organization({
                'name': 'local_organization',
                'short_name': 'organizationX',
                'description': 'Local Organization Description'
            })
        self.assertGreater(organization['id'], 0)

    def test_fetch_organization(self):
        """ Unit Test: test_fetch_organization"""
        organization1 = OrganizationFactory.create()
        organization2 = OrganizationFactory.create()
        with self.assertNumQueries(2):
            self.assertEqual(data.fetch_organization(organization1.id)['id'], organization1.id)
            self.assertEqual(data.fetch_organization(organization2.id)['id'], organization2.id)
