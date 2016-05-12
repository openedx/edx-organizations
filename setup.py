#!/usr/bin/env python

from setuptools import setup, find_packages

import organizations

setup(
    name='edx-organizations',
    version=organizations.__version__,
    description='Organization management module for Open edX',
    long_description=open('README.rst').read(),
    author='edX',
    url='https://github.com/edx/edx-organizations',
    license='AGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'django>=1.8,<1.9',
        'django-model-utils>=1.4.0,<1.5.0',
        'djangorestframework>=3.2.0,<3.4.0',
        'edx-opaque-keys>=0.1.2,<1.0.0',
        'djangorestframework-oauth>=1.1.0,<2.0.0',
        'edx-django-oauth2-provider>=0.5.0,<1.0.0',
        'edx-drf-extensions>=0.5.1,<1.0.0',
    ],
)
