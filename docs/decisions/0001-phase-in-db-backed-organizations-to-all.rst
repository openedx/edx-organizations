1. Phase In Database-Backed Organizations to All Open edX Installations
=======================================================================

Status
------

Accepted

Context
-------

Why edx-organizations exists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Originally, the concepts of "organizations" and "courses associated with organizations"
were implicit in edx-platform, being inferred from the "org" part of course/library
keys. For example, in ``course-v1:edX+DemoX+2020``, ``edX`` is the inferred organization.
There are numerous drawbacks to this being the only mechanism by which organizations exist.
Notably:

1. Efficient filtering, searching, and sorting on organization association is
   complicated, as enumerating organizations involves a full scan of all course runs
   and/or content libraries in the system.
2. Validating that course runs' "org" references point to real, intentionally-
   specified organizations is impossible. We cannot catch typos in "org" references.
3. We cannot use database-level joins to implement concepts like organization-derived
   access control.

This package was created to formalize the organization concept at a database level,
addressing the aformentioned issues.
It does so by introducing two models:

* ``Organization``, which describes an school, insitution, or other such organization.
  In edx-platform, instances are added via Django Admin or management command.
* ``OrganizationCourse``, a many-to-many join between organizations and course runs.
  In edx-platform, instances are automatically created when new course runs are created.

To ensure backwards compatibility, the installation of this packages as a Django app in
edx-platform is behind the ``FEATURES['ORGANIZATIONS_APP']`` flag, which defaults to
``False``. **Unless** that flag is specifically enabled:

* the ``Organization`` and ``OrganizationCourse`` models are unavailable,
* the functions in ``util.organizations_helpers`` (which edx-platform uses to wrap
  ``organizations.api``) will short-circuit and return ``[]`` or ``None`` for all calls, and
* validation of the "org" references when creating course runs is disabled.

Why we want to enable edx-organizations globally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although the organizations app is enabled on edx.org and stage.edx.org,
it is **not** enabled by default for Open edX installations. Notably, it is disabled
on edge.edx.org, which has 10,000+ course runs and 1,000+ content libraries.
Critically, this means that when writing edx-platform features,
we cannot assume that database-backed organizations will be available,
forcing us to write features that either:

* fall back to reasonable behavior when the organizations app is disabled, or
* put said feature behind a flag, whose enabling is dependent upon the organization app
  also being enabled.

These considerations add complexity to edx-platform feature development and roll-out.
In particular, the Blockstore-Powered Content Libraries and Taxonomies project
(a.k.a. `BD-14`_) aims to develop a new model of Blockstore-based
content libraries, which foreign-keys to the ``Organization`` model to enable
organization-based authorization and easier searching/filtering.
Making this new code tolerate the absence of database-backed organizations would require
refactoring that does not strike us as worthwhile or especially desirable.
However, we still hope to roll these new content libraries out to all Open edX instances,
including ones where the organizations app is currently disabled.

So, given all of this, **we would like to enable database-backed organizations across all Open edX
instances.**

Why that isn't simple
~~~~~~~~~~~~~~~~~~~~~

However, there is one particular aspect of enabling the organizations app
in edx-platform that would be a breaking change to anyone who does not already
enable the organizations app: **org validation**.
When ``FEATURES['ORGANIZATIONS_APP'] == True``, course runs created through
Studio must have a course key with an "org" part that maps to an organization in the
database. If one were to enable the organizations app for an instance that previously
had it disabled, then a backfill of their ``Organization`` table would need to be performed
before course runs could be created in Studio as before.


.. _BD-14: https://openedx.atlassian.net/wiki/spaces/COMM/pages/1545011241/BD-14+Blockstore+Powered+Content+Libraries+Taxonomies

Decision
--------

We want to enable database-backed organizations in edx-platform for all Open edX
instances, without an ability to disable them.
However, we do not want to force organization validation upon all Open edX instances.
So, we will **install the organizations app by default** but also
**auto-create organizations** for new course runs and libraries by default.

The organization validation behavior will only take effect when
organization auto-creation is explicitly disabled.

Finally, we will provide an **organization backfill management command**
to auto-create all missing organizations and organization-course linkages.
We will instruct operators to run it as part of the Lilac upgrade.


Consequences
------------

Overview
~~~~~~~~

The ``organizations`` app will be installed in edx-platform for all Open edX instances. This will simplify the roll-out of BD-14 and other projects that depend on database-backed organizations.

The dichotomy between the behaviors of **auto-creating missing organizations**
and **validating against missing organizations** will be toggled by a new Django flag:
``ORGANIZATIONS_AUTOCREATE``.

When ``True`` ("auto-create mode", default), the ``Organization`` model will be
treated as a **downstream source** of data for LMS/Studio, so creating content that
references a non-existant organization should cause that organization to be
automatically created in the database.

When ``False`` ("validate mode"), the ``Organization`` model will be
treated as an **authoritative source** of data for LMS/Studio,
so creating content that references
a non-existant organization should result in a validation error.


In this package (edx-organizations)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Four new Python API functions will be added:

* ``is_autocreation_enabled``: Tests and returns ``ORGANIZATIONS_AUTOCREATE``,
  as set in the Django settings of the project that installs edx-organizations
  (generally, edx-platform). Also checks ``not FEATURES["ORGANIZATIONS_APP"]`` for
  backwards-compatibility. Defaults to ``True``.
* ``ensure_organization``: Given an organization's short name, try to fetch that
  organization's details. If it does not exist, then either raise an exception
  ("auto-create mode") or create a new organization ("validate mode").
* ``get_course_organization[_id]``: Get the first organization that a course was linked
  to. This addition is tangential, but it allows us to finish ripping out
  the ``organizations_helpers`` wrapper layer that edx-platform had put around edx-organizations.

The package vesion will be bumped from 5.2.0 to 5.3.0. It is a minor version bump to signify
the lack of breaking changes.

These changes will be made in `pull request 137`_.

.. _pull request 137: https://github.com/openedx/edx-organizations/pull/137

After one edx-platform release, Version 6.0.0 of this package can be released,
which would remove the now-unnecessary check for ``FEATURES["ORGANIZATIONS_APP"]``.

In edx-platform
~~~~~~~~~~~~~~~

``organizations`` will be installed into LMS and Studio as a default app instead of as an optional app.

A management command will be added to backfill the
``Organization`` and ``OrganizationCourse`` table based on the course runs and content
libraries in the system.

The ``ORGANIZATIONS_AUTOCREATE`` toggle will be added to ``cms/envs/common.py`` with
a default value of ``True``.

The ``FEATURES["ORGANIATIONS_APP"]`` toggle will be removed.

The new ``organizations.api.ensure_organization`` function will be used to either
auto-create or raise when organizations are missing during course run and
content library creation.

The ``util.organizations_helpers`` module, which wrapped ``organizations.api``
functions to support the app's optionality, will be completely removed, and all
references will be updated to use ``organizations.api`` directly.

These changes will be made in `pull request 25153`_.

.. _pull request 25153: https://github.com/openedx/edx-platform/pull/25153

Community
~~~~~~~~~

The community will be informed of the change via both Discourse and the release notes for Lilac.
Instructions for migration will be included.

`DEPR-117`_ is created to track the eventual removal of the ``FEATURES["ORGANIATIONS_APP"]``, which
will also be part of Lilac.

.. _DEPR-117: https://openedx.atlassian.net/browse/DEPR-117

edX Ops
~~~~~~~

With the help of SRE, the organizations backfill will be run for edge.edx.org.

For edx.org and stage.edx.org, the ``FEATURES["ORGANIATIONS_APP"] = True``
overrides will be updated to be ``ORGANIZATIONS_AUTOCREATE = False``
in `pull request 3456`_.

.. _pull request 3456: https://github.com/openedx/edx/pull/3456

See also
--------

There exists a distilled, less technical version of this ADR `on the edX wiki`_.

.. _on the edX wiki: https://openedx.atlassian.net/wiki/spaces/AC/pages/2103083026/Global+roll-out+of+database-backed+Organizations
