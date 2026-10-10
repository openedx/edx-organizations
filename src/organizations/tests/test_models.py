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
        super().setUp()
        self.organization = OrganizationFactory.create()

    @ddt.data(
        [" ", ",", "@", "(", "!", "#", "$", "%", "^", "&", "*", "+", "=", "{", "[", "ó"]
    )
    def test_clean_error(self, invalid_char_list):
        """
        Verify that the clean method raises validation error if org short name
        consists of special characters or spaces.
        """
        for char in invalid_char_list:
            self.organization.short_name = f'shortname{char}'
            self.assertRaises(ValidationError, self.organization.clean)

    @ddt.data(
        ["shortnamewithoutspace", "shortName123", "short_name", "short-name", "short.name"]
    )
    def test_clean_success(self, valid_short_name_list):
        """
        Verify that the clean method returns None if org short name is valid
        """
        for valid_short_name in valid_short_name_list:
            self.organization.short_name = valid_short_name
            self.assertEqual(self.organization.clean(), None)
