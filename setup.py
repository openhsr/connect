#!/usr/bin/env python
# encoding: utf-8

import os
from setuptools import setup, find_packages


setup(
    name="openhsr-connect",
    version="0.1.15",
    packages=['openhsr_connect'],
    author="open\HSR",
    author_email="connect@openhsr.ch",
    url="https://github.com/openhsr/connect",
    description="Die Offene HSR-Mapper Alternative",
    long_description=("For more information, please checkout the `Github Page "
                      "<https://github.com/openhsr/connect>`_."),
    license="GPLv3",
    platforms=["Linux", "BSD", "MacOS"],
    include_package_data=True,
    zip_safe=False,
    install_requires=['pysmb', 'click', 'ruamel.yaml', 'keyring', 'jsonschema'],
    test_suite='tests',
    entry_points={
        'console_scripts':
            ['openhsr-connect = openhsr_connect.__main__:main']
    },

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        "Programming Language :: Python :: Implementation :: CPython",
        'Development Status :: 4 - Beta',
    ],
)
