# -*- coding: utf-8 -*-
"""
Organizations API Module Test Cases
"""
from unittest.mock import patch

import ddt
from django.test import override_settings
from opaque_keys.edx.keys import CourseKey

import organizations.api as api
import organizations.exceptions as exceptions
import organizations.tests.utils as utils


@ddt.ddt
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
            'short_name': 'test_organization',
            'name': 'test_organizationßßß',
            'description': 'Test Organization Descriptionßßß'
        })

    def test_add_organization(self):
        """ Unit Test: test_add_organization"""
        with self.assertNumQueries(3):
            organization = api.add_organization({
                'short_name': 'local_organization',
                'name': 'local_organizationßßß',
                'description': 'Local Organization Descriptionßßß'
            })
        self.assertGreater(organization['id'], 0)

    def test_add_organization_active_exists(self):
        """ Unit Test: test_add_organization_active_exists"""
        organization_data = {
            'short_name': 'local_organization',
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
            'short_name': 'local_organization',
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
            'short_name': 'local_organization',
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

    @ddt.data(
        # Empty short name
        {
            'short_name': '',
            'name': 'local_organizationßßß',
            'description': 'Local Organization Description 2ßßß'
        },
        # Empty name
        {
            'short_name': 'local_organization',
            'name': '',
            'description': 'Local Organization Description 2ßßß'
        },
        # Missing short name
        {
            'name': 'local_organizationßßß',
            'description': 'Local Organization Description 2ßßß'
        },
        # Missing name
        {
            'short_name': 'local_organization',
            'description': 'Local Organization Description 2ßßß'
        },
    )
    def test_add_organization_invalid_data_throws_exceptions(self, organization_data):
        """ Unit Test: test_add_organization_invalid_data_throws_exceptions"""
        with self.assertNumQueries(0):
            with self.assertRaises(exceptions.InvalidOrganizationException):
                api.add_organization(organization_data)

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
            'short_name': 'Orgx1',
            'description': 'Local Organization 1 Descriptionßßß'
        })
        api.add_organization({
            'name': 'local_organization_2ßßß',
            'short_name': 'Orgx2',
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


class BulkAddOrganizationsTestCase(utils.OrganizationsTestCaseBase):
    """
    Tests for `api.bulk_add_organizations`.
    """

    def test_validation_errors(self):
        """
        Test the `bulk_add_organizations` raises validation errors on bad input,
        and no organizations are created.
        """
        with self.assertRaises(exceptions.InvalidOrganizationException):
            api.bulk_add_organizations([
                self.make_organization_data("valid_org"),
                {"description": "org with no short_name!"},
            ])
        assert len(api.get_organizations()) == 0

    def test_add_no_organizations(self):
        """
        Test that `bulk_add_organizations` is a no-op when given an empty list.
        """
        api.bulk_add_organizations([])
        assert len(api.get_organizations()) == 0

    def test_edge_cases(self):
        """
        Test that bulk_add_organizations handles a few edge cases as expected.
        """
        # Add three orgs, and remove all but the first.
        api.add_organization(self.make_organization_data("existing_org"))
        api.remove_organization(
            api.add_organization(
                self.make_organization_data("org_to_reactivate")
            )["id"]
        )
        api.remove_organization(
            api.add_organization(
                self.make_organization_data("org_to_leave_inactive")
            )["id"]
        )

        # 1 query to load list of existing orgs, 1 query for create, and 1 query for update.
        with self.assertNumQueries(3):
            api.bulk_add_organizations([

                # New organization.
                self.make_organization_data("org_X"),

                # Modify existing active organization; should be no-op.
                {
                    **self.make_organization_data("existing_org"),
                    "description": "this name should be ignored"
                },

                # Deleted organizations are still stored in the DB as "inactive".
                # Bulk-adding should reactivate it.
                self.make_organization_data("org_to_reactivate"),

                # Another new organizaiton.
                self.make_organization_data("org_Y"),

                # Another org with same short name (case-insensitively)
                # as first new organization; should be ignored.
                {**self.make_organization_data("ORG_x"), "name": "this name should be ignored"}
            ])

        # There should exist the already-existing org, the org that existed as inactive
        # but is not activated, and the two new orgs.
        # This should not include `org_to_leave_inactive`.
        organizations = api.get_organizations()
        assert {
            organization["short_name"] for organization in organizations
        } == {
            "existing_org", "org_to_reactivate", "org_X", "org_Y"
        }

        # Organization dicts with already-taken short_names shouldn't have modified
        # the existing orgs.
        assert "this name should be ignored" not in {
            organization["name"] for organization in organizations
        }

    def test_add_several_organizations(self):
        """
        Test that the query_count of bulk_add_organizations does not increase
        when given more organizations.
        """
        existing_org = api.add_organization(self.make_organization_data("existing_org"))

        # 1 query to load list of existing orgs,
        # 1 query for activate-existing, and 1 query for create-new.
        with self.assertNumQueries(3):
            api.bulk_add_organizations([
                existing_org,
                existing_org,
                existing_org,
                self.make_organization_data("new_org_1"),
                self.make_organization_data("new_org_2"),
                self.make_organization_data("new_org_3"),
                self.make_organization_data("new_org_4"),
                self.make_organization_data("new_org_5"),
                self.make_organization_data("new_org_6"),
                self.make_organization_data("new_org_7"),
                self.make_organization_data("new_org_8"),
                self.make_organization_data("new_org_9"),
                self.make_organization_data("new_org_9"),  # Redundant.
                self.make_organization_data("new_org_9"),  # Redundant.
            ])
        assert len(api.get_organizations()) == 10


class BulkAddOrganizationCoursesTestCase(utils.OrganizationsTestCaseBase):
    """
    Tests for `api.bulk_add_organization_courses`.
    """

    def test_validation_errors(self):
        """
        Test the `bulk_add_organization_courses` raises validation errors on bad input,
        and no organization-course linkages are created.
        """
        valid_org = self.make_organization_data("valid_org")
        invalid_org = {"description": "org with no short_name!"}
        valid_course_key = "course-v1:a+b+c"
        invalid_course_key = "NOT-A-COURSE-KEY"

        # Any bad org data or bad course key should cause the bulk-add to raise.
        with self.assertRaises(exceptions.InvalidCourseKeyException):
            api.bulk_add_organization_courses([
                (valid_org, valid_course_key),
                (valid_org, invalid_course_key),
            ])
        with self.assertRaises(exceptions.InvalidOrganizationException):
            api.bulk_add_organization_courses([
                (valid_org, valid_course_key),
                (invalid_org, valid_course_key),
            ])

        # In either case, no data should've been written for `valid_org`.
        assert len(api.get_organization_courses(valid_org)) == 0

    def test_add_no_organizations(self):
        """
        Test that `bulk_add_organization_courses` works given an an empty list.
        """
        # 1 query to load list of existing org-courses.
        with self.assertNumQueries(1):
            api.bulk_add_organization_courses([])

    def test_edge_cases(self):
        """
        Test that bulk_add_organization_courses handles a few edge cases as expected.
        """
        org_a = api.add_organization(self.make_organization_data("org_a"))
        org_b = api.add_organization(self.make_organization_data("org_b"))
        course_key_x = CourseKey.from_string("course-v1:x+x+x")
        course_key_y = CourseKey.from_string("course-v1:y+y+y")
        course_key_z = CourseKey.from_string("course-v1:z+z+z")

        # Add linkage A->X
        api.add_organization_course(org_a, course_key_x)

        # Add and then remove (under the hood: deactivate) linkage between A->Y.
        api.add_organization_course(org_a, course_key_y)
        api.remove_organization_course(org_a, course_key_y)

        # Add and then remove (under the hood: deactivate) linkage between A->Z.
        api.add_organization_course(org_a, course_key_z)
        api.remove_organization_course(org_a, course_key_z)

        # 1 query to load list of existing org-courses,
        # 1 query for activate-existing, and 1 query for create-new.
        with self.assertNumQueries(3):
            api.bulk_add_organization_courses([

                # A->X: Existing linkage, should be a no-op.
                (org_a, course_key_x),

                # B->Y: Should create new linkage.
                (org_b, course_key_y),

                # A->Y: Is an inactive linkage; should be re-activated.
                (org_a, course_key_y),

                # B->Y: Is already in this list; shouldn't affect anything.
                (org_b, course_key_y),

                # B->Z: Adding with a stringified course id; should work as if we
                #       used the course key object.
                (org_b, str(course_key_z)),

                # B->Z: Adding again with the course key object; should be a no-op.
                (org_b, course_key_z),
            ])

        # Org A was linked to courses X and Y.
        # Org A also has an inactive link to course Z that we never re-activated.
        org_a_courses = api.get_organization_courses(org_a)
        assert {
            org_course["course_id"] for org_course in org_a_courses
        } == {
            "course-v1:x+x+x", "course-v1:y+y+y"
        }

        # Org B was linked to courses Y and Z.
        org_b_courses = api.get_organization_courses(org_b)
        assert {
            org_course["course_id"] for org_course in org_b_courses
        } == {
            "course-v1:y+y+y", "course-v1:z+z+z"
        }

    def test_add_several_organization_courses(self):
        """
        Test that the query_count of bulk_add_organization_courses does not increase
        when given more organization-course linkages to add.
        """
        org_a = api.add_organization(self.make_organization_data("org_a"))
        org_b = api.add_organization(self.make_organization_data("org_b"))
        org_c = api.add_organization(self.make_organization_data("org_c"))
        course_key_x = CourseKey.from_string("course-v1:x+x+x")
        course_key_y = CourseKey.from_string("course-v1:y+y+y")
        course_key_z = CourseKey.from_string("course-v1:z+z+z")

        # Add linkage A->X.
        api.add_organization_course(org_a, course_key_x)

        # 1 query to load list of existing org-courses,
        # 1 query for activate-existing, and 1 query for create-new.
        with self.assertNumQueries(3):
            api.bulk_add_organization_courses([
                (org_a, course_key_x),  # Already existing.
                (org_a, course_key_x),  # Already existing.
                (org_a, course_key_y),  # The rest are new.
                (org_a, course_key_z),
                (org_b, course_key_x),
                (org_b, course_key_y),
                (org_b, course_key_z),
                (org_c, course_key_x),
                (org_c, course_key_y),
                (org_c, course_key_z),
                (org_c, course_key_z),  # Redundant.
                (org_c, course_key_z),  # Redundant.
            ])
        assert len(api.get_organization_courses(org_a)) == 3
        assert len(api.get_organization_courses(org_b)) == 3
        assert len(api.get_organization_courses(org_c)) == 3
