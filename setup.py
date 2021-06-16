# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
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
            'documents = sonar.modules.documents.cli.documents:documents',
            'ark = sonar.modules.ark.cli:ark',
            'oaiharvester = \
                sonar.modules.documents.cli.oaiharvester:oaiharvester',
            'utils = sonar.modules.cli:utils',
            'es = sonar.elasticsearch.cli:es',
            'heg = sonar.heg.cli:heg',
            'resources = sonar.resources.cli:resources'
        ],
        'invenio_base.apps': [
            'sonar = sonar.ext:Sonar',
            'documents = sonar.modules.documents:Documents',
            'shibboleth_authenticator = \
                sonar.modules.shibboleth_authenticator:ShibbolethAuthenticator',
        ],
        'invenio_base.api_apps': [
            'sonar = sonar.ext:SonarAPI',
            'documents = sonar.modules.documents:Documents',
            'organisations = sonar.modules.organisations:Organisations',
            'invenio_i18n = invenio_i18n:InvenioI18N'
        ],
        'invenio_base.blueprints': [
            'sonar = sonar.theme.views:blueprint',
            'documents = sonar.modules.documents.views:blueprint',
            'users = sonar.modules.users.views:blueprint',
            'shibboleth_authenticator = \
                sonar.modules.shibboleth_authenticator.views.client:blueprint',
            'pdf_extractor = \
                sonar.modules.pdf_extractor.views.client:blueprint',
            'validation = sonar.modules.validation.views:blueprint',
            'collections = sonar.modules.collections.views:blueprint',
            'dedicated = sonar.dedicated.views:blueprint'
        ],
        'invenio_base.api_blueprints': [
            'pdf_extractor = sonar.modules.pdf_extractor.views.api:blueprint',
            'deposits = sonar.modules.deposits.rest:blueprint',
            'users = sonar.modules.users.views:blueprint',
            'monitoring = sonar.monitoring.views:blueprint',
            'translations = sonar.translations.rest:blueprint',
            'suggestions = sonar.suggestions.rest:blueprint',
            'validation = sonar.modules.validation.views:blueprint'
        ],
        'invenio_assets.webpack': [
            'sonar_theme = sonar.theme.webpack:theme'
        ],
        'invenio_config.module': [
            'sonar = sonar.config',
            'sonar_documents = sonar.modules.documents.config',
            'shibboleth_authenticator = \
                sonar.modules.shibboleth_authenticator.config',
            'pdf_extractor = sonar.modules.pdf_extractor.config',
        ],
        'invenio_i18n.translations': [
            'messages = sonar',
            'messages_wiki = flask_wiki'
        ],
        'invenio_jsonschemas.schemas': [
            'documents = sonar.modules.documents.jsonschemas',
            'organisations = sonar.modules.organisations.jsonschemas',
            'users = sonar.modules.users.jsonschemas',
            'deposits = sonar.modules.deposits.jsonschemas',
            'projects = sonar.resources.projects.jsonschemas',
            'projects_hepvs = sonar.dedicated.hepvs.projects.jsonschemas',
            'collections = sonar.modules.collections.jsonschemas',
            'subdivisions = sonar.modules.subdivisions.jsonschemas',
            'common = sonar.common.jsonschemas'
        ],
        'invenio_search.mappings': [
            'documents = sonar.modules.documents.mappings',
            'organisations = sonar.modules.organisations.mappings',
            'users = sonar.modules.users.mappings',
            'deposits = sonar.modules.deposits.mappings',
            'projects = sonar.resources.projects.mappings',
            'collections = sonar.modules.collections.mappings',
            'subdivisions = sonar.modules.subdivisions.mappings'
        ],
        'invenio_search.templates': [
            'base-record = sonar.es_templates:list_es_templates'
        ],
        'invenio_pidstore.minters': [
            'document_id = \
                sonar.modules.documents.api:document_pid_minter',
            'organisation_id = \
                sonar.modules.organisations.api:organisation_pid_minter',
            'user_id = \
                sonar.modules.users.api:user_pid_minter',
            'deposit_id = \
                sonar.modules.deposits.api:deposit_pid_minter',
            'collections_id = \
                sonar.modules.collections.api:pid_minter',
            'subdivisions_id = \
                sonar.modules.subdivisions.api:pid_minter'
        ],
        'invenio_pidstore.fetchers': [
            'document_id = \
                sonar.modules.documents.api:document_pid_fetcher',
            'organisation_id = \
                sonar.modules.organisations.api:organisation_pid_fetcher',
            'user_id = \
                sonar.modules.users.api:user_pid_fetcher',
            'deposit_id = \
                sonar.modules.deposits.api:deposit_pid_fetcher',
            'collections_id = \
                sonar.modules.collections.api:pid_fetcher',
            'subdivisions_id = \
                sonar.modules.subdivisions.api:pid_fetcher',
        ],
        "invenio_records.jsonresolver": [
            "organisation = sonar.modules.organisations.jsonresolvers",
            "user = sonar.modules.users.jsonresolvers",
            "document = sonar.modules.documents.jsonresolvers",
            "project = sonar.resources.projects.jsonresolvers",
            "collections = sonar.modules.collections.jsonresolvers",
            "subdivisions = sonar.modules.subdivisions.jsonresolvers"
        ],
        'invenio_celery.tasks' : [
            'documents = sonar.modules.documents.tasks'
        ],
        'babel.extractors': [
            'json = sonar.modules.babel_extractors:extract_json'
        ],
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
