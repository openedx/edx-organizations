"""
api.py is an interface module for Python-level integration with the
edx-organizations app.

In the current incarnation of this particular application, the API
operations are equivalent to the orchestration layer, which manages
the application's workflows.
"""
import logging

from django.conf import settings

from . import data
from . import exceptions
from . import validators


log = logging.getLogger(__name__)


# PRIVATE/INTERNAL FUNCTIONS

def _validate_course_key(course_key):
    """ Validation helper """
    if not validators.course_key_is_valid(course_key):
        exceptions.raise_exception(
            "CourseKey",
            course_key,
            exceptions.InvalidCourseKeyException
        )


def _validate_organization_data(organization_data):
    """ Validation helper """
    if not validators.organization_data_is_valid(organization_data):
        exceptions.raise_exception(
            "Organization",
            organization_data,
            exceptions.InvalidOrganizationException
        )


# PUBLIC FUNCTIONS
def add_organization(organization_data):
    """
    Passes a new organization to the data layer for storage
    """
    _validate_organization_data(organization_data)
    organization = data.create_organization(organization_data)
    return organization


def bulk_add_organizations(organization_data_items, dry_run=False, activate=True):
    """
    Efficiently store multiple organizations.

    Note: No `pre_save` or `post_save` signals for `Organization` will be
    triggered. This is due to the underlying Django implementation of `bulk_create`:
    https://docs.djangoproject.com/en/2.2/ref/models/querysets/#bulk-create

    Arguments:

        organizations (iterable[dict]):

            An iterable of `organization` dictionaries, each in the following format:
            {
                'short_name': string,
                'name': string,
                'description': string (optional),
                'logo': string (optional),
            }

            Organizations that do not already exist (by short_name) will be created.
            Organizations that already exist (by short_name) will be activated,
            but their name, description, and logo will be left as-is in the database.

            If multiple organizations share a `short_name`, the first organization
            in `organization_data_items` will be used, and the latter ones ignored.

        dry_run (bool):
            Optional, defaulting to False.
            If True, don't apply changes, but still return organizations
            that would have been created or reactivated.

        activate (bool):
            Optional, defaulting to True.
            If True, missing organizations will be created with active=True,
            and existing-but-inactive organizations will be reactivated.
            If False, missing organizations will be created with active=False,
            and existing-but-inactive organizations will be left as inactive.

    Raises:
        InvalidOrganizationException: One or more organization dictionaries
            have missing or invalid data; no organizations were created.

    Returns: tuple[set[str], set[str]]

        A tuple in the form: (
            short names of organizations that were newly created,
            short names of organizations that we reactivated
        )
        If `activate` was supplied as False, the set of reactivated linkages will
        always be empty.

        From an API layer point of view, the organizations that were "added"
        is the union of the organizations that were *newly created* and those
        that were *reactivated*. We distinguish between them in the return
        value to allow for richer reporting by users of this function.
    """
    for organization_data in organization_data_items:
        _validate_organization_data(organization_data)
        if "short_name" not in organization_data:
            raise exceptions.InvalidOrganizationException(
                f"Organization is missing short_name: {organization_data}"
            )
    return data.bulk_create_organizations(
        organization_data_items, dry_run=dry_run, activate=activate
    )


def edit_organization(organization_data):
    """
    Passes an updated organization to the data layer for storage
    """
    _validate_organization_data(organization_data)
    return data.update_organization(organization_data)


def get_organization(organization_id):
    """
    Retrieves the specified organization
    """
    return data.fetch_organization(organization_id)


def get_organization_by_short_name(organization_short_name):
    """
    Retrieves the organization filtered by short name
    """
    return data.fetch_organization_by_short_name(organization_short_name)


def get_organizations():
    """
    Retrieves the active organizations managed by the system
    """
    return data.fetch_organizations()


def remove_organization(organization_id):
    """
    Removes the specified organization
    """
    organization = {
        'id': organization_id,
    }
    data.delete_organization(organization)


def add_organization_course(organization_data, course_key):
    """
    Adds a organization-course link to the system
    """
    _validate_course_key(course_key)
    _validate_organization_data(organization_data)
    data.create_organization_course(
        organization=organization_data,
        course_key=course_key
    )


def bulk_add_organization_courses(
        organization_course_pairs,
        dry_run=False,
        activate=True,
):
    """
    Efficiently store multiple organization-course relationships.

    Note: No `pre_save` or `post_save` signals for `OrganizationCourse` will be
    triggered. This is due to the underlying Django implementation of `bulk_create`:
    https://docs.djangoproject.com/en/2.2/ref/models/querysets/#bulk-create

    Arguments:

        organization_course_pairs (iterable[tuple[dict, CourseKey]]):

            An iterable of (organization_data, course_key) pairs.

            We will ensure that these organization-course linkages exist.

            Assumption: All provided organizations already exist in storage.

        dry_run (bool):
            Optional, defaulting to False.
            If True, don't apply changes, but still return organization-course
            linkages that would have been created or reactivated.

        activate (bool):
            Optional, defaulting to True.
            If True, missing linkages will be created with active=True,
            and existing-but-inactive linkages will be reactivated.
            If False, missing linkages will be created with active=False,
            and existing-but-inactive linkages will be left as inactive.

    Raises:
        InvalidOrganizationException: One or more organization dictionaries
            have missing or invalid data.
        InvalidCourseKeyException: One or more course keys could not be parsed.
        (in case of either exception, no org-course linkages are created).

    Returns: tuple[
                set[tuple[str, CourseKey],
                set[tuple[str, CourseKey]
            ]

        A tuple in the form: (
            organization-course linkages that we newly created,
            organization-course linkages that we reactivated
        )
        where the `str` objects are organization short names.
        If `activate` was supplied as False, the set of reactivated linkages will
        always be empty.

        From an API layer point of view, the organization-
        course linkages that were "added" is the union of the linkages that were
        *newly created* and those that were *reactivated*.
        We distinguish between them in the return value to allow for richer
        reporting by users of this function.
    """
    for organization_data, course_key in organization_course_pairs:
        _validate_organization_data(organization_data)
        if "short_name" not in organization_data:
            raise exceptions.InvalidOrganizationException(
                f"Organization is missing short_name: {organization_data}"
            )
        _validate_course_key(course_key)
    return data.bulk_create_organization_courses(
        organization_course_pairs, dry_run=dry_run, activate=activate
    )


def get_organization_courses(organization_data):
    """
    Retrieves the set of courses for a given organization
    Returns an array of course identifiers
    """
    _validate_organization_data(organization_data)
    return data.fetch_organization_courses(organization=organization_data)


def remove_organization_course(organization, course_key):
    """
    Removes the specfied course from the specified organization
    """
    _validate_organization_data(organization)
    _validate_course_key(course_key)
    return data.delete_organization_course(course_key=course_key, organization=organization)


def get_course_organizations(course_key):
    """
    Retrieves the set of organizations for a given course
    Returns an array of dicts containing organizations
    """
    _validate_course_key(course_key)
    return data.fetch_course_organizations(course_key=course_key)


def get_course_organization(course_key):
    """
    Returns the first organization linked to a given course,
    or None if the course is not linked to any organizations.
    """
    _validate_course_key(course_key)
    course_organization = get_course_organizations(course_key)
    if course_organization:
        return course_organization[0]
    return None


def get_course_organization_id(course_key):
    """
    Returns the id of the first organization linked to a given course,
    or None if the course is not linked to any organizations.
    """
    course_org = get_course_organization(course_key)
    return course_org["id"] if course_org else None


def remove_course_references(course_key):
    """
    Removes course references from application state
    See edx-platform/lms/djangoapps/courseware/management/commands/delete_course_references.py
    """
    _validate_course_key(course_key)
    data.delete_course_references(course_key)


def ensure_organization(organization_short_name):
    """
    Ensure that an organization with the given short name exists.

    If the organization exists, then return it.
    If the organization does not exist, then:
        (a) If auto-create is enabled, create & return a new organization.
        (b) If auto-create is disabled, raise an InvalidOrganizationException.

    Arguments:
        organization_short_name (str)

    Returns: dict
        dictionary containing organization data

    Raises:
        InvalidOrganizationException (only if auto-create is disabled)
    """
    try:
        return get_organization_by_short_name(organization_short_name)
    except exceptions.InvalidOrganizationException:
        if not is_autocreate_enabled():
            raise
    log.info("Automatically creating new organization '%s'.", organization_short_name)
    return add_organization({
        "short_name": organization_short_name,
        "name": organization_short_name,
    })


def is_autocreate_enabled():
    """
    Return whether automatic organization creation is enabled.

    If True (default), calls to ``ensure_organization`` will auto-create organizations
    that do not already exist in the database.

    If False, calls to ``ensure_organization`` will fail for organizations that are not
    already in the database.
    """
    try:
        return bool(settings.ORGANIZATIONS_AUTOCREATE)
    except AttributeError:
        return True
