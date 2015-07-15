edx-organizations [![Build Status](https://travis-ci.org/edx/edx-organizations.svg?branch=master)](https://travis-ci.org/edx/edx-organizations) [![Coverage Status](https://img.shields.io/coveralls/edx/edx-organizations.svg)](https://coveralls.io/r/edx/edx-organizations?branch=master)
===================

edx-organizations (`organizations`) is a Django application responsible for managing the concept of Organizations in the Open edX platform.  Organizations represent the entities responsible for creating and publishing Courses.  In the future the scope and responsibilty of the Organization may evolve to include other aspects, such as related learners.

Usage
-----
*  Organizations is designed to centralize metadata about course publishers, such as their title, logo URL, and information included in certificates.


Standalone Testing
------------------

        $ ./run_tests


Open edX Platform Integration
-----------------------------
* Add desired commit hash from github code repository
    * edx-platform/requirements/github.txt
    * "Our libraries" section
* Add 'organizations' to the list of installed apps:
    * common.py
    * Feature flag convention is preferred
* In edx-platform devstack:
    * pip install -r requirements
    * paver test_system -s lms


How to Contribute
-----------------
Contributions are very welcome, but please note that edx-organizations is currently an
early stage work-in-progress and is changing frequently at this time.

See our
[CONTRIBUTING](https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst)
file for more information -- it also contains guidelines for how to maintain
high code quality, which will make your contribution more likely to be accepted.


Reporting Security Issues
-------------------------
Please do not report security issues in public. Please email security@edx.org.


Mailing List and IRC Channel
----------------------------
You can discuss this code on the [edx-code Google Group](https://groups.google.com/forum/#!forum/edx-code) or in the
`edx-code` IRC channel on Freenode.
