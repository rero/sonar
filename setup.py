# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""SONAR is a future archive of scholarly publications. It intends to collect,
promote and preserve the publications of authors affiliated with Swiss public
research institutions"""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("sonar", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="sonar",
    version=version,
    description=__doc__,
    long_description=readme,
    keywords="sonar Invenio",
    license="MIT",
    author="RERO",
    author_email="software@rero.ch",
    url="https://github.com/rero/sonar",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": ["sonar = invenio_app.cli:cli"],
        "flask.commands": ["fixtures = sonar.modules.cli:fixtures"],
        "invenio_base.apps": ["documents = sonar.modules.documents:Documents"],
        "invenio_base.blueprints": [
            "sonar = sonar.theme.views:blueprint",
            "documents = sonar.modules.documents.views:blueprint",
        ],
        "invenio_assets.webpack": ["sonar_theme = sonar.theme.webpack:theme"],
        "invenio_config.module": [
            "sonar = sonar.config",
            "sonar_app = sonar.modules.config",
            "sonar_documents = sonar.modules.documents.config",
        ],
        "invenio_i18n.translations": ["messages = sonar"],
        "invenio_base.api_apps": [
            "documents = sonar.modules.documents:Documents",
            "institutions = sonar.modules.institutions:Institutions",
        ],
        "invenio_jsonschemas.schemas": [
            "documents = sonar.modules.documents.jsonschemas",
            "institutions = sonar.modules.institutions.jsonschemas",
        ],
        "invenio_search.mappings": [
            "documents = sonar.modules.documents.mappings",
            "institutions = sonar.modules.institutions.mappings",
        ],
        "invenio_pidstore.minters": [
            "document_id = \
                sonar.modules.documents.api:document_pid_minter",
            "institution_id = \
                sonar.modules.institutions.api:institution_pid_minter",
        ],
        "invenio_pidstore.fetchers": [
            "document_id = \
                sonar.modules.documents.api:document_pid_fetcher",
            "institution_id = \
                sonar.modules.institutions.api:institution_pid_fetcher",
        ],
        "invenio_records.jsonresolver": [
            "institution = sonar.modules.institutions.jsonresolvers"
        ],
    },
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 3 - Alpha",
    ],
    setup_requires=["pytest-runner>=3.0.0,<5"],
    tests_require=["pytest-invenio>=1.0.0,<1.1.0"],
)
