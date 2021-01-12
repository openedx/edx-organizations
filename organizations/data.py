# pylint: disable=expression-not-assigned
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
import logging

from django.db.models.functions import Lower

from . import exceptions
from . import models as internal
from . import serializers


log = logging.getLogger(__name__)


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


def _activate_organization(organization_id):
    """
    Activates an inactivated (soft-deleted) organization as well as any inactive relationships
    """
    [_activate_organization_course_relationship(record) for record
     in internal.OrganizationCourse.objects.filter(organization_id=organization_id, active=False)]

    [_activate_record(record) for record
     in internal.Organization.objects.filter(id=organization_id, active=False)]


def _inactivate_organization(organization_id):
    """
    Inactivates an activated organization as well as any active relationships
    """
    [_inactivate_organization_course_relationship(record) for record
     in internal.OrganizationCourse.objects.filter(organization_id=organization_id, active=True)]

    [_inactivate_record(record) for record
     in internal.Organization.objects.filter(id=organization_id, active=True)]


def _activate_organization_course_relationship(relationship):  # pylint: disable=invalid-name
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


def _inactivate_organization_course_relationship(relationship):  # pylint: disable=invalid-name
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
        'short_name': string,
        'name': string,
        'description': string (optional),
        'logo': string (optional),
    }

    If an organization with the given `short_name` already exists, we will just
    activate that organization, but not update it.

    Returns an updated dictionary including a new 'id': integer field/value
    """
    if not (organization.get('name') and organization.get('short_name')):
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    organization_obj = serializers.deserialize_organization(organization)
    try:
        organization = internal.Organization.objects.get(
            short_name=organization_obj.short_name,
        )
        # If the organization exists, but was inactivated, we can simply turn it back on
        if not organization.active:
            _activate_organization(organization.id)
    except internal.Organization.DoesNotExist:
        organization = internal.Organization.objects.create(
            short_name=organization_obj.short_name,
            name=organization_obj.name,
            description=organization_obj.description,
            logo=organization_obj.logo,
            active=True
        )
    return serializers.serialize_organization(organization)


def bulk_create_organizations(organizations, dry_run=False, activate=True):
    """
    Efficiently insert multiple organizations into the database.

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
            in `organizations` will be used, and the latter ones ignored.

        dry_run (bool):
            Optional, defaulting to False.
            If True, don't apply changes, but still return organizations
            that would have been created or reactivated.

        activate (bool):
            Optional, defaulting to True.
            If True, missing organizations will be created with active=True,
            and existing-but-inactivate organizations will be reactivated.
            If False, missing organizations will be created with active=False,
            and existing-but-inactivate organizations will be left as inactivate.

    Returns: tuple[set[str], set[str]]

        A tuple in the form: (
            short names of organizations that were newly created,
            short names of organizations that we reactivated
        )
        If `activate` was supplied as False, the set of reactivated organizations
        will always be empty.
    """
    # Collect organizations by short name, dropping conflicts as necessary.
    organization_objs = [
        # This deserializes the dictionaries into Organization instances that
        # have not yet been saved to the db.
        serializers.deserialize_organization(organization_dict)
        for organization_dict in organizations
    ]
    # Make sure `active` is set correctly on the deserialized organizations.
    for organization_obj in organization_objs:
        organization_obj.active = activate
    organizations_by_short_name = {}
    for organization in organization_objs:
        # Make sure to lowercase short_name because MySQL UNIQUE is case-insensitive.
        short_name_lower = organization.short_name.lower()
        # Purposefully drop lowered short_names we've already seen, as noted in docstring.
        org_with_same_short_name = organizations_by_short_name.get(short_name_lower)
        if org_with_same_short_name:
            log.info(
                "Dropping organization from bulk_create batch, "
                "as an organization with the same short_name is already being "
                "created in this batch. Dropped data: %r. Kept data: %r.",
                serializers.serialize_organization(organization),
                serializers.serialize_organization(org_with_same_short_name),
            )
            continue
        organizations_by_short_name[short_name_lower] = organization

    # Find out which organizations we need to reactivate vs. create.
    existing_organizations = query_organizations_by_short_name(organizations_by_short_name)
    existing_organization_short_names = {
        short_name.lower()
        for short_name
        in existing_organizations.values_list("short_name", flat=True)
    }
    organizations_to_create = [
        organization
        for short_name, organization in organizations_by_short_name.items()
        if short_name.lower() not in existing_organization_short_names
    ]
    if activate:
        organizations_to_reactivate = existing_organizations.filter(active=False)
    else:
        organizations_to_reactivate = internal.Organization.objects.none()

    # Collect sets of orgs that will be reactivated and created,
    # so that we can have an informative return value.
    short_names_of_organizations_to_reactivate = set(
        organizations_to_reactivate.values_list("short_name", flat=True)
    )
    short_names_of_organizations_to_create = {
        org.short_name for org in organizations_to_create
    }

    # If not a dry run,
    # re-activate existing organizations, and create the new ones.
    # If `activate==False`, then `organizations_to_reactivate` will be empty.
    if not dry_run:
        organizations_to_reactivate.update(active=True)
        internal.Organization.objects.bulk_create(organizations_to_create)

    return (
        short_names_of_organizations_to_create,
        short_names_of_organizations_to_reactivate,
    )


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
    _inactivate_organization(organization_obj.id)


def fetch_organization(organization_id):
    """
    Retrieves a specific organization from app/local state
    Returns a dictionary representation of the object
    """
    organization = {'id': organization_id}
    if not organization_id:
        exceptions.raise_exception("organization", organization, exceptions.InvalidOrganizationException)
    organizations = serializers.serialize_organizations(
        internal.Organization.objects.filter(id=organization_id, active=True)
    )
    if not organizations:
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
    if not organizations:
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
            course_id=str(course_key)
        )
        # If the relationship exists, but was inactivated, we can simply turn it back on
        if not relationship.active:
            _activate_organization_course_relationship(relationship)
    except internal.OrganizationCourse.DoesNotExist:
        relationship = internal.OrganizationCourse.objects.create(
            organization=organization_obj,
            course_id=str(course_key),
            active=True
        )


def bulk_create_organization_courses(
        organization_course_pairs,
        dry_run=False,
        activate=True,
):
    """
    Efficiently insert multiple organization-course relationships into the database.

    Arguments:

        organization_course_pairs (iterable[tuple[dict, CourseKey]]):

            An iterable of (organization_data, course_key) pairs.

            Organization-course linkages that DO NOT already exist will be created.
            Organization-course linkages that DO already exist will be activated, if inactive.

            Assumption: All provided organizations already exist in the DB.

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

    Returns: tuple[
                set[tuple[str, str]],
                set[tuple[str, str]]
             ]

        A tuple in the form: (
            organization-course linkages that we newly created,
            organization-course linkages that we reactivated
        )
        where an "organization-course" linkage is a tuple in the form:
            (organization short name, course key string).
        If `activate` was supplied as False, the set of reactivated linkages will
        always be empty.
    """
    def linkage_to_pair(linkage):
        """
        Given a `OrganizationCourse` (aka org-course linkage) instance,
        return a pair of strings:
        (lowercased organization short name, stringified course key)

        We normalize short_names to lowercase because MySQL UNIQUE is case-insensitive.
        """
        return linkage.organization.short_name.lower(), linkage.course_id

    # Grab all org-course linkages from db (whether active or inactive).
    db_linkages = list(
        internal.OrganizationCourse.objects.all().prefetch_related(
            'organization'
        )
    )

    # For the organizations that have been requested for creation,
    # build a set of (lowered org shortname, course key string) linkage pairs.
    # This will remove any duplicates.
    requested_linkage_pairs = {
        (organization_data["short_name"].lower(), str(course_key))
        for organization_data, course_key
        in organization_course_pairs
    }

    # Build the same set of pairs for linkages already in the db.
    db_linkage_pairs = {
        linkage_to_pair(linkage) for linkage in db_linkages
    }

    # The set of org-course linkages that we must CREATE
    # is the set of linkages that were REQUESTED
    # minus the set of linkages in the DATABASE.
    linkage_pairs_to_create = requested_linkage_pairs - db_linkage_pairs

    # The set of org-course linkages that we must ENSURE ARE ACTIVE
    # is the set of linkages that were REQUESTED
    # minus the set of linkages that WILL BE CREATED,
    # unless activate==False, in which case we won't ensure anything is active.
    if activate:
        linkage_pairs_to_ensure_active = requested_linkage_pairs - linkage_pairs_to_create
    else:
        linkage_pairs_to_ensure_active = set()

    # The linkages we must REACTIVATE
    # are those that we must ENSURE ARE ACTIVE
    # and are currently INACTIVE.
    linkages_to_reactivate = [
        linkage
        for linkage in db_linkages
        if (
            linkage_to_pair(linkage) in linkage_pairs_to_ensure_active
            and not linkage.active
        )
    ]

    # If this is a dry run, return before applying any changes to the db.
    linkage_pairs_to_reactivate = {
        linkage_to_pair(linkage)
        for linkage in linkages_to_reactivate
    }
    if dry_run:
        return linkage_pairs_to_create, linkage_pairs_to_reactivate

    # Bulk-reactivate existing organization-course linkages.
    # If `ids_of_linkages_to_reactivate` is an empty set, then this is a no-op.
    ids_of_linkages_to_reactivate = {linkage.id for linkage in linkages_to_reactivate}
    internal.OrganizationCourse.objects.filter(
        id__in=ids_of_linkages_to_reactivate
    ).update(
        active=True
    )

    # Load up a dict: (org short names, Organization model instances).
    # We need these Organizations so we can create linkages against them in the
    # next step.
    organizations_for_create = query_organizations_by_short_name(
        org for org, _ in linkage_pairs_to_create
    )
    organizations_for_create_by_short_name = {
        organization.short_name.lower(): organization
        for organization in organizations_for_create
    }

    # Bulk-create new organization-course linkages.
    internal.OrganizationCourse.objects.bulk_create([
        internal.OrganizationCourse(
            organization=organizations_for_create_by_short_name[org_short_name],
            course_id=course_id,
            active=activate,
        )
        for org_short_name, course_id
        in linkage_pairs_to_create
    ])
    return linkage_pairs_to_create, linkage_pairs_to_reactivate


def query_organizations_by_short_name(short_names):
    """
    Get a queryset of organizations from an iterable of organiztion short names.

    This is meant as a utility function for the bulk-create functions.
    It is not currently exposed through the API, but it could be.

    Canonicalize short names to lowercase due to case-insensitivity of
    MySQL UNIQUE constraint on `short_name`.

    Arguments:
        short_names (Iterable[str])

    Returns: QuerySet[Organization]
    """
    unique_short_names = {short_name.lower() for short_name in short_names}
    return internal.Organization.objects.annotate(
        short_name_lowered=Lower("short_name")
    ).filter(
        short_name_lowered__in=unique_short_names,
    )


def delete_organization_course(organization, course_key):
    """
    Removes an existing organization-course relationship from app/local state
    No response currently defined for this operation
    """
    try:
        relationship = internal.OrganizationCourse.objects.get(
            organization=organization['id'],
            course_id=str(course_key),
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
        course_id=str(course_key),
        active=True
    ).select_related('organization')
    return [serializers.serialize_organization_with_course(organization) for organization in queryset]


def delete_course_references(course_key):
    """
    Inactivates references to course keys within this app (ref: receivers.py and api.py)
    """
    [_inactivate_record(record) for record in internal.OrganizationCourse.objects.filter(
        course_id=str(course_key),
        active=True
    )]
