#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup
import setuptools


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="inmanta-terraform-module-generator",
    version="0.1.0",
    author="Inmanta",
    author_email="code@inmanta.com",
    maintainer="Inmanta",
    maintainer_email="code@inmanta.com",
    license="Inmanta EULA",
    description="Tool to generate inmanta modules from their terraform provider counter-part",
    long_description=read("README.md"),
    packages=setuptools.find_packages(where='src'),
    package_dir={"": "src"},
    include_package_data=False,
    python_requires="~=3.9",
    install_requires=[
        "inmanta-module-factory",
        "inmanta-module-terraform",
        "msgpack",
        "requests",
        "nltk",
        "click",
        "PyYAML",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
