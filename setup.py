#!/usr/bin/env python

from setuptools import setup

setup(
    name='edx-organizations',
    version='0.1.1',
    description='Significant events module for Open edX',
    long_description=open('README.md').read(),
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
    packages=['organizations'],
    dependency_links=[
    ],
    install_requires=[
        "django>=1.4.12",
        "django-model-utils==1.4.0",
        "South>=0.7.6",
    ],
    tests_require=[
        "coverage==3.7.1",
        "nose==1.3.3",
        "httpretty==0.8.0",
        "pep8==1.5.7",
        "pylint==1.2.1",
        "pep257==0.3.2"
    ]
)
