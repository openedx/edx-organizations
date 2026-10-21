"""
Application-specific exception classes used throughout the implementation
"""
from django.core.exceptions import ValidationError


class InvalidCourseKeyException(ValidationError):
    """ CourseKey validation exception class """


class InvalidOrganizationException(ValidationError):
    """ Organization validation exception class """


def raise_exception(entity_type, entity, exception):
    """ Exception helper """
    raise exception(
        f'The {entity_type} you have provided is not valid: {entity}'.encode('utf-8')
    )
