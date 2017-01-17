# pylint: disable=too-many-public-methods
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
