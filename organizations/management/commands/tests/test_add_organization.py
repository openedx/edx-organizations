"""
Tests for organization-adding management command.
"""
from django.core.management import call_command, CommandError
from django.test import TestCase

from organizations.models import Organization


class TestAddOrganizationCommand(TestCase):
    """ Tests for add_organization.Command. """

    ORG_SHORT_NAME = "msw"
    ORG_NAME = "Ministry of Silly Walks"

    def assert_one_active_organization(self, short_name, name):
        """
        Assert that there is exactly one organization with the given short_name,
        and if so, that it has the specified name and is active.
        """
        # Fails with MultipleObjectsReturned if >1 orgs matching `short_name`
        org = Organization.objects.get(short_name=short_name)
        self.assertEqual(org.name, name)
        self.assertTrue(org.active)

    def test_add_org(self):
        call_command('add_organization', self.ORG_SHORT_NAME, self.ORG_NAME)
        self.assert_one_active_organization(self.ORG_SHORT_NAME, self.ORG_NAME)

    def test_add_same_org_twice(self):
        call_command('add_organization', self.ORG_SHORT_NAME, self.ORG_NAME)
        call_command('add_organization', self.ORG_SHORT_NAME, self.ORG_NAME)
        self.assert_one_active_organization(self.ORG_SHORT_NAME, self.ORG_NAME)

    def test_add_existing_org(self):
        Organization.objects.create(
            short_name=self.ORG_SHORT_NAME, name=self.ORG_NAME, active=False
        )
        call_command('add_organization', self.ORG_SHORT_NAME, self.ORG_NAME)
        self.assert_one_active_organization(self.ORG_SHORT_NAME, self.ORG_NAME)

    def test_bad_argument_order(self):
        with self.assertRaises(CommandError):
            call_command('add_organization', self.ORG_NAME, self.ORG_SHORT_NAME)
