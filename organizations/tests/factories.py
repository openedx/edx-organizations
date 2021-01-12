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

    username = factory.Sequence('robot{}'.format)
    email = factory.Sequence('robot+test+{}@edx.org'.format)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    first_name = factory.Sequence('Robot{}'.format)
    last_name = 'Test'
    is_staff = False
    is_active = True
    is_superuser = False


class OrganizationFactory(DjangoModelFactory):
    """ Organization creation factory."""
    class Meta:
        model = Organization

    name = factory.Sequence('organization name {}'.format)
    short_name = factory.Sequence('name{}'.format)
    description = factory.Sequence('description{}'.format)
    logo = None
    active = True
