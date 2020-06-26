# This Python file uses the following encoding: utf-8
"""
Validators confirm the integrity of inbound information prior to a data.py handoff
"""
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey


def course_key_is_valid(course_key):
    """
    Course key object validation
    """
    if course_key is None:
        return False
    try:
        CourseKey.from_string(str(course_key))
    except (InvalidKeyError, UnicodeDecodeError):
        return False
    return True


def organization_data_is_valid(organization_data):
    """
    Organization data validation
    """
    if organization_data is None:
        return False
    if 'id' in organization_data and not organization_data.get('id'):
        return False
    if 'name' in organization_data and not organization_data.get('name'):
        return False
    return True
