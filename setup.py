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
    version="0.1.1",
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
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=["tf_grpc_plugin", "msgpack"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
