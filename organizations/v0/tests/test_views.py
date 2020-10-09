"""
Organizations Views Test Cases.
"""
import json
from django.urls import reverse
from django.test import TestCase

from organizations.models import Organization
from organizations.serializers import OrganizationSerializer
from organizations.tests.factories import UserFactory, OrganizationFactory


class TestOrganizationsView(TestCase):
    """ Test Organizations View."""

    def setUp(self):
        super(TestOrganizationsView, self).setUp()

        self.user_password = 'test'
        self.user = UserFactory(password=self.user_password, is_superuser=True)
        self.organization = OrganizationFactory.create()
        self.organization_list_url = reverse('v0:organization-list')
        self.client.login(username=self.user.username, password=self.user_password)

    def _get_organization_url(self, organization):
        """ Return organization specific URL."""
        return reverse('v0:organization-detail', kwargs={'short_name': organization.short_name})

    def test_authentication_required(self):
        """ Verify that authentication is required to access view."""
        self.client.logout()
        response = self.client.get(self.organization_list_url)
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user(self):
        """ Verify that the authenticated user gets data."""
        OrganizationFactory.create()
        response = self.client.get(self.organization_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_single_organization(self):
        """verify single organization data could be fetched using short name"""
        url = self._get_organization_url(self.organization)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, OrganizationSerializer(self.organization).data)

    def test_inactive_organization(self):
        """ Verify inactive organization are filtered out."""
        organization = OrganizationFactory(active=False)
        url = self._get_organization_url(organization)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_organization(self):
        """ Verify that nonexistent organization have proper status code."""
        url = reverse('v0:organization-detail', kwargs={'short_name': 'dummy'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_organization(self):
        """ Verify Organization can be created via PUT endpoint. """
        data = {
            'name': 'example-name',
            'short_name': 'example-short-name',
            'description': 'example-description',
        }
        url = reverse('v0:organization-detail', kwargs={'short_name': data['short_name']})
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['short_name'], data['short_name'])
        self.assertEqual(response.data['description'], data['description'])
        orgs = Organization.objects.all()
        self.assertEqual(len(orgs), 2)

    def test_update_organization(self):
        """ Verify Organization can be updated via PUT endpoint. """
        org = OrganizationFactory()
        data = {
            'name': 'changed-name',
            'short_name': org.short_name,
        }
        url = reverse('v0:organization-detail', kwargs={'short_name': org.short_name})
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['short_name'], org.short_name)
        self.assertEqual(response.data['description'], org.description)
        orgs = Organization.objects.all()
        self.assertEqual(len(orgs), 2)

    def test_patch_endpoint(self):
        """ Verify PATCH endpoint returns 405 because we use PUT for create and update"""
        url = reverse('v0:organization-detail', kwargs={'short_name': 'dummy'})
        response = self.client.patch(url, json={})
        self.assertEqual(response.status_code, 405)

    def test_create_as_only_staff_user(self):
        self.user.is_staff = True
        self.user.is_superuser = False
        self.user.save()

        data = {
            'name': 'example-name',
            'short_name': 'example-short-name',
            'description': 'example-description',
        }
        url = reverse('v0:organization-detail', kwargs={'short_name': data['short_name']})
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_create_as_non_staff_and_non_admin_user(self):
        self.user.is_superuser = False
        self.user.save()

        data = {
            'name': 'example-name',
            'short_name': 'example-short-name',
            'description': 'example-description',
        }
        url = reverse('v0:organization-detail', kwargs={'short_name': data['short_name']})
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
