"""
Utility module for Organizations test cases
"""
from django.test import TestCase

from opaque_keys.edx.keys import CourseKey


class OrganizationsTestCaseBase(TestCase):
    """
    Parent/Base class for Organizations test cases
    """

    def setUp(self):
        """
        Helper method for test case scaffolding
        """
        super(OrganizationsTestCaseBase, self).setUp()
        self.test_course_key = CourseKey.from_string('the/course/key')

    @staticmethod
    def make_organization_data(short_name):
        """
        Make a fake organization dictionary, distinguished by a `short_name`.

        The `short_name` should be a valid short_name string, i.e. [0-9a-z_-].
        """
        return {
            'short_name': short_name,
            'name': "Name of {}".format(short_name),
            'description': "Description of {}".format(short_name),
        }
