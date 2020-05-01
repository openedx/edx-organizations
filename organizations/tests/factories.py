"""
Provides factory for User.
"""
from django.contrib.auth.models import User
import factory
from factory.django import DjangoModelFactory

from organizations.models import Organization


class UserFactory(DjangoModelFactory):
    """ User creation factory."""
    class Meta:
        model = User
        django_get_or_create = ('email', 'username')

    username = factory.Sequence(u'robot{0}'.format)
    email = factory.Sequence(u'robot+test+{0}@edx.org'.format)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    first_name = factory.Sequence(u'Robot{0}'.format)
    last_name = 'Test'
    is_staff = False
    is_active = True
    is_superuser = False


class OrganizationFactory(DjangoModelFactory):
    """ Organization creation factory."""
    class Meta:
        model = Organization

    name = factory.Sequence(u'organization name {}'.format)
    short_name = factory.Sequence(u'name{}'.format)
    description = factory.Sequence(u'description{}'.format)
    logo = None
    active = True
