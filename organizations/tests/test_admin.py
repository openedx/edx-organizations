"""
Organizations Admin Module Test Cases
"""

from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

import organizations.tests.utils as utils
from organizations.admin import OrganizationAdmin, OrganizationCourseAdmin
from organizations.models import Organization, OrganizationCourse
from organizations.tests.factories import UserFactory


def create_organization(index, active=True):
    """
    Create an organization.
    """
    Organization.objects.create(
        short_name=f'test_org_{index}',
        name=f'test organization {index}',
        description='test organization description',
        active=active
    )


class OrganizationsAdminTestCase(utils.OrganizationsTestCaseBase):
    """
    Test Case module for Organizations Admin
    """

    def setUp(self):
        super().setUp()
        self.org_admin = OrganizationAdmin(Organization, AdminSite())
        self.request = RequestFactory().get('/admin')
        self.admin_user = UserFactory(is_staff=True)
        self.request.session = 'session'
        self.request.user = self.admin_user
        self.request._messages = FallbackStorage(self.request)  # pylint: disable=protected-access

    def test_default_fields(self):
        """
        Test: organization default fields should be name, description and active.
        """
        self.assertEqual(list(self.org_admin.get_form(self.request).base_fields),
                         ['name', 'short_name', 'description', 'logo', 'active'])

    def test_organization_actions(self):
        """
        Test: organization should have its custom actions.
        """
        actions = self.org_admin.get_actions(self.request)
        self.assertIn('activate_selected', actions.keys())
        self.assertIn('deactivate_selected', actions.keys())
        self.assertNotIn('delete_selected', actions.keys())

    def test_deactivate_selected_should_deactivate_active_organizations(self):
        """
        Test: action deactivate_selected should deactivate an activated organization.
        """
        create_organization(1, active=True)
        queryset = Organization.objects.filter(pk=1)
        self.org_admin.deactivate_selected(self.request, queryset)
        self.assertFalse(Organization.objects.get(pk=1).active)

    def test_deactivate_selected_should_deactivate_multiple_active_organizations(self):
        """
        Test: action deactivate_selected should deactivate the multiple activated organization.
        """
        for i in range(2):
            create_organization(i, active=True)
        queryset = Organization.objects.all()
        self.org_admin.deactivate_selected(self.request, queryset)
        self.assertFalse(Organization.objects.get(pk=1).active)
        self.assertFalse(Organization.objects.get(pk=2).active)

    def test_activate_selected_should_activate_deactivated_organizations(self):
        """
        Test: action activate_selected should activate an deactivated organization.
        """
        create_organization(1, active=False)
        queryset = Organization.objects.filter(pk=1)
        self.org_admin.activate_selected(self.request, queryset)
        self.assertTrue(Organization.objects.get(pk=1).active)

    def test_activate_selected_should_activate_multiple_deactivated_organizations(self):
        """
        Test: action activate_selected should activate the multiple deactivated organization.
        """
        for i in range(2):
            create_organization(i, active=True)
        queryset = Organization.objects.all()
        self.org_admin.activate_selected(self.request, queryset)
        self.assertTrue(Organization.objects.get(pk=1).active)
        self.assertTrue(Organization.objects.get(pk=2).active)


class OrganizationCourseAdminTestCase(utils.OrganizationsTestCaseBase):
    """
    Test Case module for Organization Course Admin
    """

    def setUp(self):
        super().setUp()
        self.request = RequestFactory().get('')
        self.org_course_admin = OrganizationCourseAdmin(OrganizationCourse, AdminSite())

    def test_foreign_key_field_active_choices(self):
        """
        Test: organization course foreignkey widget has active organization choices.
        """
        create_organization(1, active=True)
        self.assertEqual(
            list(self.org_course_admin.get_form(self.request).base_fields['organization'].widget.choices),
            [('', '---------'), (1, 'test organization 1 (test_org_1)')]
        )

    def test_foreign_key_field_inactive_choices(self):
        """
        Test: organization course foreignkey widget has not inactive organization choices.
        """
        create_organization(1, active=False)
        self.assertEqual(
            list(self.org_course_admin.get_form(self.request).base_fields['organization'].widget.choices),
            [('', '---------')]
        )
