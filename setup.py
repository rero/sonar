# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.

"""SONAR is a future archive of scholarly publications. It intends to collect,
promote and preserve the publications of authors affiliated with Swiss public
research institutions"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('sonar', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='sonar',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='sonar Invenio',
    license='MIT',
    author='RERO',
    author_email='software@rero.ch',
    url='https://github.com/rero/sonar',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'sonar = invenio_app.cli:cli',
        ],
        'flask.commands': [
            'fixtures = sonar.modules.cli:fixtures',
            'utils = sonar.modules.cli:utils'
        ],
        'invenio_base.apps': [
            'sonar = sonar.modules:Sonar',
            'shibboleth_authenticator = \
                sonar.modules.shibboleth_authenticator:ShibbolethAuthenticator',
        ],
        'invenio_base.blueprints': [
            'sonar = sonar.theme.views:blueprint',
            'documents = sonar.modules.documents.views:blueprint',
            'shibboleth_authenticator = \
                sonar.modules.shibboleth_authenticator.views.client:blueprint',
            'pdf_extractor = \
                sonar.modules.pdf_extractor.views.client:blueprint'
        ],
        'invenio_base.api_blueprints': [
            'sonar = sonar.theme.api_views:blueprint',
            'pdf_extractor = sonar.modules.pdf_extractor.views.api:blueprint',
            'deposits = sonar.modules.deposits.rest:blueprint'
        ],
        'invenio_assets.webpack': [
            'sonar_theme = sonar.theme.webpack:theme'
        ],
        'invenio_config.module': [
            'sonar = sonar.config',
            'sonar_app = sonar.modules.config',
            'sonar_documents = sonar.modules.documents.config',
            'shibboleth_authenticator = \
                sonar.modules.shibboleth_authenticator.config',
            'pdf_extractor = sonar.modules.pdf_extractor.config',
        ],
        'invenio_i18n.translations': [
            'messages = sonar',
        ],
        'invenio_base.api_apps': [
            'documents = sonar.modules.documents:Documents',
            'institutions = sonar.modules.institutions:Institutions',
            'sonar = sonar.modules:Sonar'
        ],
        'invenio_jsonschemas.schemas': [
            'documents = sonar.modules.documents.jsonschemas',
            'institutions = sonar.modules.institutions.jsonschemas',
            'users = sonar.modules.users.jsonschemas',
            'deposits = sonar.modules.deposits.jsonschemas'
        ],
        'invenio_search.mappings': [
            'documents = sonar.modules.documents.mappings',
            'institutions = sonar.modules.institutions.mappings',
            'users = sonar.modules.users.mappings',
            'deposits = sonar.modules.deposits.mappings'
        ],
        'invenio_search.templates': [
            'base-record = sonar.es_templates:list_es_templates'
        ],
        'invenio_pidstore.minters': [
            'document_id = \
                sonar.modules.documents.api:document_pid_minter',
            'institution_id = \
                sonar.modules.institutions.api:institution_pid_minter',
            'user_id = \
                sonar.modules.users.api:user_pid_minter',
            'deposit_id = \
                sonar.modules.deposits.api:deposit_pid_minter'
        ],
        'invenio_pidstore.fetchers': [
            'document_id = \
                sonar.modules.documents.api:document_pid_fetcher',
            'institution_id = \
                sonar.modules.institutions.api:institution_pid_fetcher',
            'user_id = \
                sonar.modules.users.api:user_pid_fetcher',
            'deposit_id = \
                sonar.modules.deposits.api:deposit_pid_fetcher'
        ],
        "invenio_records.jsonresolver": [
            "institution = sonar.modules.institutions.jsonresolvers",
            "user = sonar.modules.users.jsonresolvers"
        ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ]
)
