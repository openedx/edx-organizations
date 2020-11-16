edx-organizations |Build Status| |Coverage Status|
==================================================

edx-organizations (``organizations``) is a Django application
responsible for managing the concept of Organizations in the Open edX
platform. Organizations represent the entities responsible for creating
and publishing Courses. In the future the scope and responsibilty of the
Organization may evolve to include other aspects, such as related
learners.

.. |Build Status| image:: https://travis-ci.com/edx/edx-organizations.svg?branch=master
   :target: https://travis-ci.com/edx/edx-organizations
.. |Coverage Status| image:: https://coveralls.io/repos/github/edx/edx-organizations/badge.svg?branch=master
   :target: https://coveralls.io/github/edx/edx-organizations?branch=master

Usage
-----
Organizations is designed to centralize metadata about course publishers, such as their title, logo URL,
and information included in certificates.

Local Development
-----------------

.. code-block:: bash

    $ make requirements
    $ make test
    $ make quality

Open edX Platform Integration
-----------------------------

1. Update the version of ``edx-organizations`` in the appropriate requirements file (e.g. ``requirements/edx/base.txt``).
2. Add ‘organizations’ to the list of installed apps in ``common.py``.
3. Install all requirements:

.. code-block:: bash

   $ pip install -r requirements

4. (Optional) Run tests:

.. code-block:: bash

   $ paver test_system -s lms

How to Contribute
-----------------
Contributions are very welcome, but please note that edx-organizations is currently an early stage
work-in-progress and is changing frequently at this time.

See our `CONTRIBUTING`_ file for more information – it also contains guidelines for how to
maintain high code quality, which will make your contribution more likely to be accepted.

.. _CONTRIBUTING: https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst

Reporting Security Issues
-------------------------
Please do not report security issues in public. Please email security@edx.org.

Mailing List and IRC Channel
----------------------------

You can discuss this code on the `edx-code Google Group`_ or in the
``edx-code`` IRC channel on Freenode.

.. _edx-code Google Group: https://groups.google.com/forum/#!forum/edx-code
