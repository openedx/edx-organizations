# -*- coding: utf-8 -*-
"""
Organizations API Module Test Cases
"""
from unittest.mock import patch

from django.test import override_settings

import organizations.api as api
import organizations.exceptions as exceptions
import organizations.tests.utils as utils


class OrganizationsApiTestCase(utils.OrganizationsTestCaseBase):
    """
    Main Test Case module for Organizations API
    """
    def setUp(self):
        """
        Organizations API Test Case scaffolding
        """
        super(OrganizationsApiTestCase, self).setUp()
        self.test_organization = api.add_organization({
            'name': 'test_organizationßßß',
            'description': 'Test Organization Descriptionßßß'
        })

    def test_add_organization(self):
        """ Unit Test: test_add_organization"""
        with self.assertNumQueries(3):
            organization = api.add_organization({
                'name': 'local_organizationßßß',
                'description': 'Local Organization Descriptionßßß'
            })
        self.assertGreater(organization['id'], 0)

    def test_add_organization_active_exists(self):
        """ Unit Test: test_add_organization_active_exists"""
        organization_data = {
            'name': 'local_organizationßßß',
            'description': 'Local Organization Descriptionßßß'
        }
        organization = api.add_organization(organization_data)
        self.assertGreater(organization['id'], 0)
        with self.assertNumQueries(1):
            organization = api.add_organization(organization_data)

    def test_add_organization_inactive_to_active(self):
        """ Unit Test: test_add_organization_inactive_to_active"""
        organization_data = {
            'name': 'local_organizationßßß',
            'description': 'Local Organization Descriptionßßß'
        }
        organization = api.add_organization(organization_data)
        self.assertGreater(organization['id'], 0)
        api.remove_organization(organization['id'])

        with self.assertNumQueries(5):
            organization = api.add_organization(organization_data)

        # Assert that the organization is active by making sure we can load it.
        loaded_organization = api.get_organization(organization['id'])
        self.assertEqual(loaded_organization['name'], organization_data['name'])

    def test_add_organization_inactive_organization_with_relationships(self):
        """ Unit Test: test_add_organization_inactive_organization_with_relationships"""
        organization_data = {
            'name': 'local_organizationßßß',
            'description': 'Local Organization Descriptionßßß'
        }
        organization = api.add_organization(organization_data)
        api.add_organization_course(
            organization,
            self.test_course_key
        )

        with self.assertNumQueries(1):
            organization = api.add_organization(organization_data)

    def test_add_organization_invalid_data_throws_exceptions(self):
        """ Unit Test: test_add_organization_invalid_namespaces_throw_exceptions"""
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.add_organization({
                    'name': '',  # Empty name should throw an exception on create
                    'description': 'Local Organization Description 2ßßß'
                })

        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.add_organization({
                    # Missing name should throw exception
                    'description': 'Local Organization Description 2ßßß'
                })

    def test_edit_organization(self):
        """ Unit Test: test_edit_organization"""
        self.test_organization['name'] = 'Edited Organizationßßß'

        with self.assertNumQueries(1):
            api.edit_organization(self.test_organization)

    def test_edit_organization_invalid_data_throws_exceptions(self):
        """ Unit Test: test_edit_organization_invalid_data_throws_exceptions """
        self.test_organization['name'] = ''
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.edit_organization(self.test_organization)

        self.test_organization['id'] = 0
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.edit_organization(self.test_organization)

    def test_edit_organization_bogus_organization(self):
        """ Unit Test: test_edit_organization_bogus_organization """
        self.test_organization['id'] = 12345
        self.test_organization['name'] = 'bogus.organizationsßßß'
        with self.assertNumQueries(1):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.edit_organization(self.test_organization)
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.edit_organization(None)

    def test_get_organization(self):
        """ Unit Test: test_get_organization"""
        with self.assertNumQueries(1):
            organization = api.get_organization(self.test_organization['id'])
        self.assertEqual(organization['name'], self.test_organization['name'])
        self.assertEqual(organization['description'], self.test_organization['description'])

    def test_get_organization_by_short_name(self):
        """ Unit Test: get_organization_by_short_name"""
        api.add_organization({
            'name': 'local_organization_1ßßß',
            'short_name': 'Orgx1',
            'description': 'Local Organization 1 Descriptionßßß'
        })
        api.add_organization({
            'name': 'local_organization_2',
            'short_name': 'Orgx2',
            'description': 'Local Organization 2'
        })
        with self.assertNumQueries(1):
            organization = api.get_organization_by_short_name('Orgx2')
        self.assertEqual(organization['name'], 'local_organization_2')
        self.assertEqual(organization['description'], 'Local Organization 2')

        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.get_organization_by_short_name(None)

        with self.assertNumQueries(1):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.get_organization_by_short_name('not_existing')

    def test_get_organizations(self):
        """ Unit Test: test_get_organizations """
        api.add_organization({
            'name': 'local_organization_1ßßß',
            'description': 'Local Organization 1 Descriptionßßß'
        })
        api.add_organization({
            'name': 'local_organization_2ßßß',
            'description': 'Local Organization 2 Descriptionßßß'
        })
        with self.assertNumQueries(1):
            organizations = api.get_organizations()
        self.assertEqual(len(organizations), 3)  # One from SetUp, two from local

    def test_get_organization_invalid_organization(self):
        """ Unit Test: test_get_organization_invalid_organization """
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.get_organization(None)
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.get_organization(0)

    def test_remove_organization(self):
        """ Unit Test: test_remove_organization """
        with self.assertNumQueries(4):
            api.remove_organization(self.test_organization['id'])
        with self.assertRaises(exceptions.InvalidOrganizationException):
            api.get_organization(self.test_organization['id'])

    def test_remove_organization_bogus_organization(self):
        """ Unit Test: test_remove_organization_bogus_organization """
        with self.assertNumQueries(4):
            api.remove_organization(self.test_organization['id'])

        with self.assertRaises(exceptions.InvalidOrganizationException):
            api.get_organization(self.test_organization['id'])

        # Do it again with the valid id to hit the exception workflow
        with self.assertNumQueries(2):
            api.remove_organization(self.test_organization['id'])

        with self.assertRaises(exceptions.InvalidOrganizationException):
            api.get_organization(self.test_organization['id'])

    def test_add_organization_course(self):
        """ Unit Test: test_add_organization_course """
        with self.assertNumQueries(2):
            api.add_organization_course(
                self.test_organization,
                self.test_course_key
            )

    def test_add_organization_course_active_exists(self):
        """ Unit Test: test_add_organization_course_active_exists """
        api.add_organization_course(
            self.test_organization,
            self.test_course_key
        )
        with self.assertNumQueries(1):
            api.add_organization_course(
                self.test_organization,
                self.test_course_key
            )

    def test_add_organization_course_inactive_to_active(self):
        """ Unit Test: test_add_organization_course_inactive_to_active """
        api.add_organization_course(
            self.test_organization,
            self.test_course_key
        )
        api.remove_organization_course(self.test_organization, self.test_course_key)
        with self.assertNumQueries(3):
            api.add_organization_course(
                self.test_organization,
                self.test_course_key
            )

    def test_add_organization_course_bogus_course_key(self):
        """ Unit Test: test_add_organization_course_bogus_course_key """
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidCourseKeyException):
                api.add_organization_course(self.test_organization, '12345667avßßß')
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidCourseKeyException):
                api.add_organization_course(self.test_organization, None)

    def test_get_course_organizations(self):
        """ Unit Test: test_get_course_organizations """
        api.add_organization_course(
            self.test_organization,
            self.test_course_key
        )
        with self.assertNumQueries(1):
            course_organizations = api.get_course_organizations(self.test_course_key)
        self.assertEqual(len(course_organizations), 1)

    def test_get_course_organization_no_linked_orgs(self):
        """
        Test that when a course is linked to no organizations,
        ``get_course_organization`` and ``get_course_organization_id`` return None.
        """
        assert api.get_course_organization(self.test_course_key) is None
        assert api.get_course_organization_id(self.test_course_key) is None

    def test_get_course_organization_multi_linked_orgs(self):
        """
        Test that when a course is linked to multiple organizations,
        ``get_course_organization`` and ``get_course_organization_id``
        return the first-linked one.
        """
        # Use non-alphabetically-ordered org names to test that the
        # returned org was the first *linked*, not just the first *alphabetically*.
        api.add_organization_course(
            api.add_organization({'short_name': 'orgW', 'name': 'Org West'}),
            self.test_course_key,
        )
        api.add_organization_course(
            api.add_organization({'short_name': 'orgN', 'name': 'Org North'}),
            self.test_course_key,
        )
        api.add_organization_course(
            api.add_organization({'short_name': 'orgS', 'name': 'Org South'}),
            self.test_course_key,
        )
        org_result = api.get_course_organization(self.test_course_key)
        assert org_result['short_name'] == 'orgW'
        org_id_result = api.get_course_organization_id(self.test_course_key)
        assert org_id_result
        assert org_id_result == org_result['id']

    def test_remove_organization_course(self):
        """ Unit Test: test_remove_organization_course """
        api.add_organization_course(
            self.test_organization,
            self.test_course_key
        )
        organizations = api.get_course_organizations(self.test_course_key)
        self.assertEqual(len(organizations), 1)
        with self.assertNumQueries(3):
            api.remove_organization_course(self.test_organization, self.test_course_key)
        organizations = api.get_course_organizations(self.test_course_key)
        self.assertEqual(len(organizations), 0)

    def test_remove_organization_course_missing_organization(self):
        """ Unit Test: test_remove_organization_course_missing_organization """
        with self.assertNumQueries(1):
            api.remove_organization_course(self.test_organization, self.test_course_key)
        organizations = api.get_course_organizations(self.test_course_key)
        self.assertEqual(len(organizations), 0)

    def test_remove_organization_course_missing_course(self):
        """ Unit Test: test_remove_organization_course_missing_organization """
        api.add_organization_course(
            self.test_organization,
            'edX/DemoX/Demo_Course'
        )
        organizations = api.get_course_organizations('edX/DemoX/Demo_Course')
        self.assertEqual(len(organizations), 1)
        with self.assertNumQueries(1):
            api.remove_organization_course(self.test_organization, self.test_course_key)
        organizations = api.get_course_organizations(self.test_course_key)
        self.assertEqual(len(organizations), 0)

    def test_remove_course_references(self):
        """ Unit Test: test_remove_course_references """
        # Add a course dependency on the test organization
        api.add_organization_course(
            self.test_organization,
            self.test_course_key
        )
        self.assertEqual(len(api.get_organization_courses(self.test_organization)), 1)

        # Remove the course dependency
        with self.assertNumQueries(2):
            api.remove_course_references(self.test_course_key)
        self.assertEqual(len(api.get_organization_courses(self.test_organization)), 0)

    @patch.object(api.log, 'info')
    def test_ensure_organization_retrieves_known_org(self, mock_log_info):
        """
        Test that, with oranization auto-create enabled, ``ensure_organization``
        returns the org data of an existing organization.
        """
        api.add_organization({
            'short_name': 'myorg', 'name': 'My Org', 'description': 'this is my org'
        })
        org_data = api.ensure_organization('myorg')
        assert org_data['id']
        assert org_data['short_name'] == 'myorg'
        assert org_data['name'] == 'My Org'
        assert org_data['description'] == 'this is my org'

        # We expect a single logging message in test_ensure_organization_creates_unknown_org,
        # so check for 0 log messages here as a control.
        assert mock_log_info.call_count == 0

    @patch.object(api.log, 'info')
    def test_ensure_organization_creates_unknown_org(self, mock_log_info):
        """
        Test that, with organization auto-create enabled, ``ensure_organization``
        automatically creates not-yet-existent organizations.
        """
        org_data = api.ensure_organization('myorg')
        assert org_data['id']
        assert org_data['short_name'] == 'myorg'
        assert org_data['name'] == 'myorg'
        assert org_data['description'] == ''  # auto-created, so no description.

        # Make sure we logged about the new organization's creation.
        assert mock_log_info.call_count == 1

        # Make sure that the organization has, in fact, been saved to the database
        # by loading it up again.
        assert api.get_organization_by_short_name('myorg') == org_data

    @override_settings(ORGANIZATIONS_AUTOCREATE=False)
    def test_ensure_organization_retrieves_known_org_no_autocreate(self):
        """
        Test that, with organization auto-create DISABLED, ``ensure_organization``
        returns the org data of an existing organization
        (just like it does when organization auto-create is enabled).
        """
        api.add_organization({
            'short_name': 'myorg', 'name': 'My Org', 'description': 'this is my org'
        })
        org_data = api.ensure_organization('myorg')
        assert org_data['id']
        assert org_data['short_name'] == 'myorg'
        assert org_data['name'] == 'My Org'
        assert org_data['description'] == 'this is my org'

    @override_settings(ORGANIZATIONS_AUTOCREATE=False)
    def test_ensure_organization_raises_for_unknown_org_no_autocreate(self):
        """
        Test that, with organization auto-create DISABLED, ``ensure_organization``
        fails when given a non-existent organization
        (in contrast to how it behaves when organization auto-create is enabled).
        """
        with self.assertRaises(exceptions.InvalidOrganizationException):
            api.ensure_organization('myorg')

        # Make sure the organization was not saved to the database.
        with self.assertRaises(exceptions.InvalidOrganizationException):
            api.get_organization_by_short_name('myorg')

    def test_autocreate_enabled_by_default(self):
        """
        Test that, by default, automatic organization creation is enabled.
        """
        assert api.is_autocreate_enabled()

    @override_settings(FEATURES={"ORGANIZATIONS_APP": True})
    def test_autocreate_disabled_by_organizations_app(self):
        """
        Tests that enabling FEATURES['ORGANIZATIONS_APP'] has the effect of
        disabling automatic organization creation.
        """
        assert not api.is_autocreate_enabled()
