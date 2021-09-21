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

    username = factory.Sequence(lambda arg: f'robot{arg}')
    email = factory.Sequence(lambda arg: f'robot+test+{arg}@edx.org')
    password = factory.PostGenerationMethodCall('set_password', 'test')
    first_name = factory.Sequence(lambda arg: f'Robot{arg}')
    last_name = 'Test'
    is_staff = False
    is_active = True
    is_superuser = False


class OrganizationFactory(DjangoModelFactory):
    """ Organization creation factory."""
    class Meta:
        model = Organization

    name = factory.Sequence(lambda arg: f'organization name {arg}')
    short_name = factory.Sequence(lambda arg: f'name{arg}')
    description = factory.Sequence(lambda arg: f'description{arg}')
    logo = None
    active = True
