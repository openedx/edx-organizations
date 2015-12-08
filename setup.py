#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='edx-organizations',
    version='0.2.0',
    description='Organization management module for Open edX',
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
    packages=find_packages(exclude=["tests"]),
    dependency_links=[
    ],
    install_requires=[
        "django>=1.8",
        "django-model-utils==1.4.0",
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
