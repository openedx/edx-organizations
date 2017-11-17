# coding=utf-8
"""
Tests for Organization Model.
"""

import ddt
from django.core.exceptions import ValidationError
from django.test import TestCase
from organizations.tests.factories import OrganizationFactory


@ddt.ddt
class TestOrganizationModel(TestCase):
    """ OrganizationModel tests. """
    def setUp(self):
        super(TestOrganizationModel, self).setUp()
        self.organization = OrganizationFactory.create()

    @ddt.data(
        "short name with space",
        "short_name[with,special",
        "shórt_name"
    )
    def test_clean_error(self, short_name):
        """
        Verify that the clean method raises validation error if org short name
        consists of special characters or spaces.
        """
        self.organization.short_name = short_name
        self.assertRaises(ValidationError, self.organization.clean)

    @ddt.data(
        "shortnamewithoutspace",
        "shortName123",
        "short_name"
    )
    def test_clean_success(self, short_name):
        """
        Verify that the clean method returns None if org short name is valid
        """
        self.organization.short_name = short_name
        self.assertEqual(self.organization.clean(), None)
