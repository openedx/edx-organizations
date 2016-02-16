"""
Organizations Views Test Cases.
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from provider.constants import CONFIDENTIAL
from provider.oauth2.models import AccessToken, Client

from organizations.serializers import OrganizationSerializer
from organizations.tests.factories import UserFactory, OrganizationFactory


# pylint: disable=no-member, no-self-use
class TestOrganizationsView(TestCase):
    """ Test Organizations View."""
    def setUp(self):
        super(TestOrganizationsView, self).setUp()

        self.user_password = 'test'
        self.user = UserFactory(password=self.user_password)
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

    def test_oauth2(self):
        """Verify that the API can handle OAuth 2.0 access tokens."""
        oauth2_client = Client.objects.create(client_type=CONFIDENTIAL)
        access_token = AccessToken.objects.create(
            token='fake-access-token',
            client=oauth2_client,
            user=self.user,
        )

        self.client.logout()

        response = self.client.get(
            self.organization_list_url,
            HTTP_AUTHORIZATION='Bearer {}'.format(access_token)
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            self.organization_list_url,
            HTTP_AUTHORIZATION='Bearer {}'.format('nonexistent-access-token')
        )
        self.assertEqual(response.status_code, 401)
