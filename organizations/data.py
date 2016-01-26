# This Python file uses the following encoding: utf-8
# pylint: disable=no-member,expression-not-assigned
"""
Application data management/abstraction layer.  Responsible for:

1) Accessing information from various resources:
* Internal application state  (through local models in models.py)
* External application state  (ORM bindings with other apps, yuck)
* Remote data services (through service adapters in resources.py)

2) Calculating derivative information from existing state:
* Algorithms and data manipulations
* Aggregations
* Annotations
* Alternative data representations

Accepts and returns standard Python data structures (dicts, arrays of dicts)
for easy consumption and manipulation by callers -- the queryset stops here!

When the time comes for remote resources, import the module like so:
if getattr(settings, 'TEST_MODE', False):
    import organizations.tests.mocks.resources as remote
else:
    import organizations.resources as remote
"""
from . import exceptions
from . import models as internal
from . import serializers


# PRIVATE/INTERNAL METHODS (public methods located further down)
def _activate_record(record):
    """
    Enables database records by setting the 'active' attribute to True
    The queries in this module filter out inactive records as part of their criteria
    This effectively allows us to soft-delete records so they are not lost forever
    """
    record.active = True
    record.save()


def _inactivate_record(record):
    """
    Disables database records by setting the 'active' attribute to False
    The queries in this module filter out inactive records as part of their criteria
    This effectively allows us to soft-delete records so they are not lost forever
    """
    record.active = False
    record.save()


def _activate_organization(organization):
    """
    Activates an inactivated (soft-deleted) organization as well as any inactive relationships
    """
    [_activate_organization_course_relationship(record) for record
     in internal.OrganizationCourse.objects.filter(organization_id=organization.id, active=False)]

    [_activate_record(record) for record
     in internal.Organization.objects.filter(id=organization.id, active=False)]


def _inactivate_organization(organization):
    """
    Inactivates an activated organization as well as any active relationships
    """
    [_inactivate_organization_course_relationship(record) for record
     in internal.OrganizationCourse.objects.filter(organization_id=organization.id, active=True)]

    [_inactivate_record(record) for record
     in internal.Organization.objects.filter(id=organization.id, active=True)]


def _activate_organization_course_relationship(relationship):
    """
    Activates an inactive organization-course relationship
    """
    # If the relationship doesn't exist or the organization isn't active we'll want to raise an error
    relationship = internal.OrganizationCourse.objects.get(
        id=relationship.id,
        active=False,
        organization__active=True
    )
    _activate_record(relationship)


def _inactivate_organization_course_relationship(relationship):
    """
    Inactivates an active organization-course relationship
    """
    relationship = internal.OrganizationCourse.objects.get(
        id=relationship.id,
        active=True
    )
    _inactivate_record(relationship)


# PUBLIC METHODS
def create_organization(organization):
    """
    Inserts a new organization into app/local state given the following dictionary:
    {
        'name': string,
        'description': string
    }
    Returns an updated dictionary including a new 'id': integer field/value
    """
    # Trust, but verify...
    if not organization.get('name'):
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    organization_obj = serializers.deserialize_organization(organization)
    try:
        organization = internal.Organization.objects.get(
            name=organization_obj.name,
        )
        # If the organization exists, but was inactivated, we can simply turn it back on
        if not organization.active:
            _activate_organization(organization_obj)
    except internal.Organization.DoesNotExist:
        organization = internal.Organization.objects.create(
            name=organization_obj.name,
            short_name=organization_obj.short_name,
            description=organization_obj.description,
            logo=organization_obj.logo,
            active=True
        )
    return serializers.serialize_organization(organization)


def update_organization(organization):
    """
    Updates an existing organization in app/local state
    Returns a dictionary representation of the object
    """
    organization_obj = serializers.deserialize_organization(organization)
    try:
        organization = internal.Organization.objects.get(id=organization_obj.id)
        organization.name = organization_obj.name
        organization.short_name = organization_obj.short_name
        organization.description = organization_obj.description
        organization.logo = organization_obj.logo
        organization.active = organization_obj.active
    except internal.Organization.DoesNotExist:
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    return serializers.serialize_organization(organization)


def delete_organization(organization):
    """
    Inactivates an existing organization from app/local state
    No return currently defined for this operation
    """
    organization_obj = serializers.deserialize_organization(organization)
    _inactivate_organization(organization_obj)


def fetch_organization(organization_id):
    """
    Retrieves a specific organization from app/local state
    Returns a dictionary representation of the object
    """
    organization = {'id': organization_id}
    if not organization_id:
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    organizations = serializers.serialize_organizations(internal.Organization.objects.filter(active=True))
    if not len(organizations):
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    return organizations[0]


def fetch_organization_by_short_name(organization_short_name):
    """
    Retrieves a specific organization from app/local state by short name
    Returns a dictionary representation of the object
    """
    organization = {'short_name': organization_short_name}
    if not organization_short_name:
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    organizations = serializers.serialize_organizations(internal.Organization.objects.filter(
        active=True, short_name=organization_short_name
    ))
    if not len(organizations):
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    return organizations[0]


def fetch_organizations():
    """
    Retrieves the set of active organizations from app/local state
    Returns a list-of-dicts representation of the object
    """
    return serializers.serialize_organizations(internal.Organization.objects.filter(active=True))


def create_organization_course(organization, course_key):
    """
    Inserts a new organization-course relationship into app/local state
    No response currently defined for this operation
    """
    organization_obj = serializers.deserialize_organization(organization)
    try:
        relationship = internal.OrganizationCourse.objects.get(
            organization=organization_obj,
            course_id=unicode(course_key)
        )
        # If the relationship exists, but was inactivated, we can simply turn it back on
        if not relationship.active:
            _activate_organization_course_relationship(relationship)
    except internal.OrganizationCourse.DoesNotExist:
        relationship = internal.OrganizationCourse.objects.create(
            organization=organization_obj,
            course_id=unicode(course_key),
            active=True
        )


def delete_organization_course(organization, course_key):
    """
    Removes an existing organization-course relationship from app/local state
    No response currently defined for this operation
    """
    try:
        relationship = internal.OrganizationCourse.objects.get(
            organization=organization['id'],
            course_id=unicode(course_key),
            active=True,
        )
        _inactivate_organization_course_relationship(relationship)
    except internal.OrganizationCourse.DoesNotExist:
        # If we're being asked to delete an organization-course link
        # that does not exist in the database then our work is done
        pass


def fetch_organization_courses(organization):
    """
    Retrieves the set of courses currently linked to the specified organization
    """
    organization_obj = serializers.deserialize_organization(organization)
    queryset = internal.OrganizationCourse.objects.filter(
        organization=organization_obj,
        active=True
    ).select_related('organization')
    return [serializers.serialize_organization_with_course(organization) for organization in queryset]


def fetch_course_organizations(course_key):
    """
    Retrieves the organizations linked to the specified course
    """
    queryset = internal.OrganizationCourse.objects.filter(
        course_id=unicode(course_key),
        active=True
    ).select_related('organization')
    return [serializers.serialize_organization_with_course(organization) for organization in queryset]


def delete_course_references(course_key):
    """
    Inactivates references to course keys within this app (ref: receivers.py and api.py)
    """
    [_inactivate_record(record) for record in internal.OrganizationCourse.objects.filter(
        course_id=unicode(course_key),
        active=True
    )]
