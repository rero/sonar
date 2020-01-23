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
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Common pytest fixtures and plugins."""

import os
import tempfile

import pytest
from flask import url_for
from flask_security.utils import encrypt_password
from invenio_files_rest.models import Location
from invenio_search import current_search

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.institutions.api import InstitutionRecord


@pytest.fixture(scope='module')
def es(appctx):
    """Setup and teardown all registered Elasticsearch indices.

    Scope: module
    This fixture will create all registered indexes in Elasticsearch and remove
    once done. Fixtures that perform changes (e.g. index or remove documents),
    should used the function-scoped :py:data:`es_clear` fixture to leave the
    indexes clean for the following tests.
    """
    from invenio_search.errors import IndexAlreadyExistsError
    from invenio_search import current_search, current_search_client

    try:
        list(current_search.put_templates())
    except IndexAlreadyExistsError:
        current_search_client.indices.delete_template('*')
        list(current_search.put_templates())

    try:
        list(current_search.create())
    except IndexAlreadyExistsError:
        list(current_search.delete(ignore=[404]))
        list(current_search.create())
    current_search_client.indices.refresh()

    try:
        yield current_search_client
    finally:
        current_search_client.indices.delete(index='*')
        current_search_client.indices.delete_template('*')


@pytest.fixture(scope='module', autouse=True)
def app_config(app_config):
    """Define configuration for module."""
    app_config['SHIBBOLETH_SERVICE_PROVIDER'] = dict(
        strict=True,
        debug=True,
        entity_id='entity_id',
        x509cert='./docker/nginx/sp.pem',
        private_key='./docker/nginx/sp.key')

    app_config['SHIBBOLETH_IDENTITY_PROVIDERS'] = dict(
        idp=dict(entity_id='https://idp.com/shibboleth',
                 sso_url='https://idp.com/Redirect/SSO',
                 mappings=dict(
                     email='email',
                     full_name='name',
                     user_unique_id='id',
                 )))

    return app_config


@pytest.fixture()
def create_user(app):
    """Create user in database."""
    datastore = app.extensions['security'].datastore
    datastore.create_user(email='john.doe@test.com',
                          password=encrypt_password('123456'),
                          active=True)
    datastore.commit()


@pytest.fixture()
def logged_user_client(create_user, client):
    """Log in user."""
    response = client.post(url_for('security.login'),
                           data=dict(email='john.doe@test.com',
                                     password='123456'))
    assert response.status_code == 302

    return client


@pytest.fixture()
def organization_fixture(app, db):
    """Create an organization."""
    data = {'pid': 'org', 'name': 'Fake organization'}

    organization = InstitutionRecord.create(data, dbcommit=True)
    organization.reindex()
    db.session.commit()
    return organization


@pytest.fixture()
def document_json_fixture(app, db, organization_fixture):
    """JSON document fixture."""
    data = {
        "pid":
        "10000",
        "identifiedBy": [{
            "value": "urn:nbn:ch:rero-006-108713",
            "type": "bf:Urn"
        }, {
            "value": "oai:doc.rero.ch:20050302172954-WU",
            "type": "bf:Identifier"
        }],
        "language": [{
            "value": "eng",
            "type": "bf:Language"
        }],
        "authors": [{
            "type": "person",
            "name": "Mancini, Loriano",
            "date": "1975-03-23",
            "qualifier": "Librarian"
        }, {
            "type": "person",
            "name": "Ronchetti, Elvezio"
        }, {
            "type": "person",
            "name": "Trojani, Fabio"
        }],
        'title': [{
            'type':
            'bf:Title',
            'mainTitle': [{
                'language': 'eng',
                'value': 'Title of the document'
            }]
        }],
        "extent":
        "103 p",
        "abstracts": [{
            "language": "eng",
            "value": "Abstract of the document"
        }],
        "subjects": [{
            "language": "eng",
            "value": ["Time series models", "GARCH models"]
        }],
        "provisionActivity": [{
            'type':
            'bf:Manufacture',
            'statement': [{
                'label': [{
                    'value': 'Bienne'
                }],
                'type': 'bf:Place'
            }, {
                'label': [{
                    'value': 'Impr. Weber'
                }],
                'type': 'bf:Agent'
            }, {
                'label': [{
                    'value': '[2006]'
                }],
                'type': 'Date'
            }, {
                'label': [{
                    'value': 'Lausanne'
                }],
                'type': 'bf:Place'
            }, {
                'label': [{
                    'value': 'Rippone'
                }],
                'type': 'bf:Place'
            }, {
                'label': [{
                    'value': 'Impr. Coustaud'
                }],
                'type': 'bf:Agent'
            }]
        }],
        "editionStatement": [{
            "editionDesignation": [{
                "value": "Di 3 ban"
            }, {
                "value": "第3版",
                "language": "chi-hani"
            }],
            "responsibility": [{
                "value": "Zeng Lingliang zhu bian"
            }, {
                "value": "曾令良主编",
                "language": "chi-hani"
            }]
        }],
        "institution": {
            "$ref": "https://sonar.ch/api/institutions/org"
        }
    }

    return data


@pytest.fixture()
def document_fixture(app, db, document_json_fixture, bucket_location_fixture):
    """Create a document."""
    document = DocumentRecord.create(document_json_fixture,
                                     dbcommit=True,
                                     with_bucket=True)
    db.session.commit()
    document.reindex()

    current_search.flush_and_refresh('documents')

    return document


@pytest.fixture()
def bucket_location_fixture(app, db):
    """Create a default location for managing files."""
    tmppath = tempfile.mkdtemp()
    db.session.add(Location(name='default', uri=tmppath, default=True))
    db.session.commit()


@pytest.fixture()
def pdf_file():
    """Return test PDF file path."""
    return os.path.dirname(os.path.abspath(__file__)) + '/data/test.pdf'
