"""
Tests for Organizations API serializers.
"""


from django.test import TestCase
from rest_framework.fields import DateTimeField
from rest_framework.settings import api_settings

from organizations.serializers import OrganizationSerializer
from organizations.tests.factories import OrganizationFactory


class TestOrganizationSerializer(TestCase):
    """ OrganizationSerializer tests."""
    def setUp(self):
        super().setUp()
        self.organization = OrganizationFactory.create()

    def test_data(self):
        """ Verify that OrganizationSerializer serialize data correctly."""
        datetime_field = DateTimeField(format=api_settings.DATETIME_FORMAT)

        serialize_data = OrganizationSerializer(self.organization)
        expected = {
            "id": self.organization.id,
            "name": self.organization.name,
            "short_name": self.organization.short_name,
            "description": self.organization.description,
            "logo": None,
            "active": self.organization.active,
            "created": datetime_field.to_representation(self.organization.created),
            "modified": datetime_field.to_representation(self.organization.modified),
        }
        self.assertEqual(serialize_data.data, expected)
