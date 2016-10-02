#!/usr/bin/env python
# encoding: utf-8

import os
from setuptools import setup, find_packages


setup(
    name="openhsr-connect",
    version="0.1.0.dev0",
    packages=['openhsr_connect'],
    author="open\HSR",
    author_email="info@openhsr.ch",
    url="https://github.com/openhsr/connect",
    description="Die Offene HSR-Mapper Alternative",
    long_description=("For more information, please checkout the `Github Page "
                      "<https://github.com/altcomphsr/connect>`_."),
    license="GPLv3",
    platforms=["Linux", "BSD", "MacOS"],
    # data_files=[('', ['scripts/Generic-PostScript_Printer-Postscript.ppd', 'scripts/openhsr-connect'])],
    include_package_data=True,
    zip_safe=False,
    install_requires=open('./requirements.txt').read(),
    test_suite='tests',
    entry_points={
        'console_scripts':
            ['openhsr-connect = openhsr_connect.cli:main']
    },

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        "Programming Language :: Python :: Implementation :: CPython",
        'Development Status :: 4 - Beta',
    ],
)
