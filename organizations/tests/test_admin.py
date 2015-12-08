# pylint: disable=invalid-name
# pylint: disable=too-many-public-methods
# pylint: disable=no-member
"""
Organizations Admin Module Test Cases
"""
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
import organizations.tests.utils as utils
from organizations.admin import OrganizationAdmin, OrganizationCourseAdmin
from organizations.models import (Organization, OrganizationCourse)


def create_organization(active=True):
    """
    Create an organization.
    """
    Organization.objects.create(
        name='test organization',
        description='test organization description',
        active=active
    )


class OrganizationsAdminTestCase(utils.OrganizationsTestCaseBase):
    """
    Test Case module for Organizations Admin
    """

    def setUp(self):
        self.request = HttpRequest()
        self.orgAdmin = OrganizationAdmin(Organization, AdminSite())
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_default_fields(self):
        """
        Test: organization default fields should be name, description and active.
        """
        self.assertEqual(list(self.orgAdmin.get_form(self.request).base_fields),
                         ['name', 'short_name', 'description', 'logo', 'active'])

    def test_organization_actions(self):
        """
        Test: organization should have its custom actions.
        """
        actions = self.orgAdmin.get_actions(self.request)
        self.assertTrue('activate_selected' in actions.keys())
        self.assertTrue('deactivate_selected' in actions.keys())
        self.assertTrue('delete_selected' not in actions.keys())

    def test_deactivate_selected_should_deactivate_active_organizations(self):
        """
        Test: action deactivate_selected should deactivate an activated organization.
        """
        create_organization(active=True)
        queryset = Organization.objects.filter(pk=1)
        self.orgAdmin.deactivate_selected(self.request, queryset)
        self.assertFalse(Organization.objects.get(pk=1).active)

    def test_deactivate_selected_should_deactivate_multiple_active_organizations(self):
        """
        Test: action deactivate_selected should deactivate the multiple activated organization.
        """
        for __ in xrange(0, 2):
            create_organization(active=True)
        queryset = Organization.objects.all()
        self.orgAdmin.deactivate_selected(self.request, queryset)
        self.assertFalse(Organization.objects.get(pk=1).active)
        self.assertFalse(Organization.objects.get(pk=2).active)

    def test_activate_selected_should_activate_deactivated_organizations(self):
        """
        Test: action activate_selected should activate an deactivated organization.
        """
        create_organization(active=False)
        queryset = Organization.objects.filter(pk=1)
        self.orgAdmin.activate_selected(self.request, queryset)
        self.assertTrue(Organization.objects.get(pk=1).active)

    def test_activate_selected_should_activate_multiple_deactivated_organizations(self):
        """
        Test: action activate_selected should activate the multiple deactivated organization.
        """
        for __ in xrange(0, 2):
            create_organization(active=True)
        queryset = Organization.objects.all()
        self.orgAdmin.activate_selected(self.request, queryset)
        self.assertTrue(Organization.objects.get(pk=1).active)
        self.assertTrue(Organization.objects.get(pk=2).active)


class OrganizationCourseAdminTestCase(utils.OrganizationsTestCaseBase):
    """
    Test Case module for Organization Course Admin
    """
    def setUp(self):
        self.request = HttpRequest()
        self.orgCourseAdmin = OrganizationCourseAdmin(OrganizationCourse, AdminSite())

    def test_foreign_key_field_active_choices(self):
        """
        Test: organization course foreignkey widget has active organization choices.
        """
        create_organization(active=True)
        self.assertEqual(
            list(self.orgCourseAdmin.get_form(self.request).base_fields['organization'].widget.choices),
            [('', '---------'), (1, u'test organization')])

    def test_foreign_key_field_inactive_choices(self):
        """
        Test: organization course foreignkey widget has not inactive organization choices.
        """
        create_organization(active=False)
        self.assertEqual(
            list(self.orgCourseAdmin.get_form(self.request).base_fields['organization'].widget.choices),
            [('', '---------')])
