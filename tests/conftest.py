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
from io import BytesIO

import pytest
from flask import url_for
from flask_principal import ActionNeed
from flask_security.utils import encrypt_password
from invenio_access.models import ActionUsers, Role
from invenio_accounts.ext import hash_password
from invenio_files_rest.models import Location
from invenio_search import current_search

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.documents.api import DocumentRecord
from sonar.modules.institutions.api import InstitutionRecord
from sonar.modules.users.api import UserRecord


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
def db_user_fixture(app, db):
    """Create user in database."""
    data = {
        'email': 'user@rero.ch',
        'full_name': 'John Doe',
        'roles': ['user']
    }

    user = UserRecord.create(data, dbcommit=True)
    user.reindex()
    db.session.commit()

    return user


@pytest.fixture()
def db_moderator_fixture(app, db):
    """Create moderator in database."""
    data = {
        'email': 'moderator@rero.ch',
        'full_name': 'John Doe',
        'roles': ['moderator']
    }

    user = UserRecord.create(data, dbcommit=True)
    user.reindex()
    db.session.commit()

    return user


@pytest.fixture()
def user_without_role_fixture(app, db):
    """Create user in database without role."""
    datastore = app.extensions['security'].datastore
    user = datastore.create_user(email='user-without-role@test.com',
                                 password=hash_password('123456'),
                                 active=True)
    db.session.commit()

    return user


@pytest.fixture()
def user_fixture(app, db):
    """Create user in database."""
    datastore = app.extensions['security'].datastore
    user = datastore.create_user(email='user@test.com',
                                 password=hash_password('123456'),
                                 active=True)
    db.session.commit()

    role = Role(name='user')
    role.users.append(user)

    db.session.add(role)
    db.session.add(ActionUsers.allow(ActionNeed('user-access'), user=user))
    db.session.commit()

    return user


@pytest.fixture()
def admin_user_fixture(app, db):
    """User with admin access."""
    datastore = app.extensions['security'].datastore
    user = datastore.create_user(email='admin@test.com',
                                 password=hash_password('123456'),
                                 active=True)
    datastore.commit()

    role = Role(name='admin')
    role.users.append(user)

    db.session.add(role)
    db.session.add(ActionUsers.allow(ActionNeed('admin-access'), user=user))
    db.session.commit()

    return user


@pytest.fixture()
def superadmin_user_fixture(app, db):
    """User with admin access."""
    datastore = app.extensions['security'].datastore
    user = datastore.create_user(email='superadmin@test.com',
                                 password=hash_password('123456'),
                                 active=True)
    db.session.commit()

    role = Role(name='superadmin')
    role.users.append(user)

    db.session.add(role)
    db.session.add(ActionUsers.allow(ActionNeed('superuser-access'),
                                     user=user))
    db.session.commit()

    return user


@pytest.fixture()
def admin_user_fixture_with_db(app, db, admin_user_fixture,
                               organization_fixture):
    """Create user in database."""
    db_user = UserRecord.create(
        {
            'pid': '10000',
            'email': admin_user_fixture.email,
            'full_name': 'Jules Brochu',
            'roles': ['admin'],
            'user_id': admin_user_fixture.id,
            'institution': {
                '$ref': 'https://sonar.ch/api/institutions/org'
            }
        },
        dbcommit=True)
    db_user.reindex()
    db.session.commit()

    current_search.flush_and_refresh('users')

    return db_user


@pytest.fixture()
def document_json_fixture(app, db, organization_fixture):
    """JSON document fixture."""
    data = {
        'pid':
        '10000',
        'identifiedBy': [{
            'value': 'urn:nbn:ch:rero-006-108713',
            'type': 'bf:Urn'
        }, {
            'value': 'oai:doc.rero.ch:20050302172954-WU',
            'type': 'bf:Identifier'
        }],
        'language': [{
            'value': 'eng',
            'type': 'bf:Language'
        }],
        'authors': [{
            'type': 'person',
            'name': 'Mancini, Loriano',
            'date': '1975-03-23',
            'qualifier': 'Librarian'
        }, {
            'type': 'person',
            'name': 'Ronchetti, Elvezio'
        }, {
            'type': 'person',
            'name': 'Trojani, Fabio'
        }],
        'title': [{
            'type':
            'bf:Title',
            'mainTitle': [{
                'language': 'eng',
                'value': 'Title of the document'
            }]
        }],
        'extent':
        '103 p',
        'abstracts': [{
            'language': 'eng',
            'value': 'Abstract of the document'
        }],
        'subjects': [{
            'label': {
                'language': 'eng',
                'value': ['Time series models', 'GARCH models']
            },
            'source': 'RERO'
        }],
        'provisionActivity': [{
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
        'editionStatement': [{
            'editionDesignation': [{
                'value': 'Di 3 ban'
            }, {
                'value': '第3版',
                'language': 'chi-hani'
            }],
            'responsibility': [{
                'value': 'Zeng Lingliang zhu bian'
            }, {
                'value': '曾令良主编',
                'language': 'chi-hani'
            }]
        }],
        'institution': {
            '$ref': 'https://sonar.ch/api/institutions/org'
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
def document_with_file(app, db, document_fixture, pdf_file):
    """Create a document with a file associated."""
    with open(pdf_file, 'rb') as file:
        content = file.read()

    document_fixture.add_file(content, 'test1.pdf', order=1)

    document_fixture.commit()
    db.session.commit()

    return document_fixture


@pytest.fixture()
def deposit_fixture(app, db, db_user_fixture, pdf_file,
                    bucket_location_fixture):
    """Deposit fixture."""
    deposit_json = {
        '$schema':
        'https://sonar.ch/schemas/deposits/deposit-v1.0.0.json',
        '_bucket':
        '03e5e909-2fce-479e-a697-657e1392cc72',
        'contributors': [{
            'affiliation': 'RERO',
            'name': 'Takayoshi Shintaro',
            'orcid': 'ORCID NUMBER'
        }, {
            'name': 'Murakami Yuta'
        }, {
            'name': 'Werner Philipp'
        }],
        'metadata': {
            'abstracts': ['Abstract of the document'],
            'document_type': 'preprint',
            'etc': 'ETC field',
            'journal': {
                'name': 'American Physical Society (APS)',
                'pages': '184303',
                'volume': '99'
            },
            'languages': ['eng'],
            'publication_date': {
                'type': 'simple',
                'value': '2020-02-14'
            },
            'title': 'High-harmonic generation in quantum spin systems'
        },
        'projects': [{
            'end_date':
            '2020-02-29',
            'funding_organisation':
            'Swiss Universities',
            'name':
            'Project name',
            'related_persons': [{
                'affiliation': 'RERO',
                'name': 'John Dow',
                'type': 'principal investigator'
            }],
            'start_date':
            '2020-02-01'
        }],
        'status':
        'in progress',
        'step':
        'diffusion',
        'user': {
            '$ref':
            'https://sonar.ch/api/users/{pid}'.format(
                pid=db_user_fixture['pid'])
        }
    }

    deposit = DepositRecord.create(deposit_json,
                                   dbcommit=True,
                                   with_bucket=True)

    with open(pdf_file, 'rb') as file:
        content = file.read()

    deposit.files['main.pdf'] = BytesIO(content)
    deposit.files['main.pdf']['label'] = 'Main file'
    deposit.files['main.pdf']['category'] = 'main'
    deposit.files['main.pdf']['file_type'] = 'file'

    deposit.files['additional.pdf'] = BytesIO(content)
    deposit.files['additional.pdf']['label'] = 'Additional file 1'
    deposit.files['additional.pdf']['category'] = 'additional'
    deposit.files['additional.pdf']['file_type'] = 'file'

    deposit.commit()
    deposit.reindex()
    db.session.commit()

    current_search.flush_and_refresh('deposits')

    return deposit


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


@pytest.fixture(autouse=True)
def mock_thumbnail_creation(monkeypatch):
    """Mock thumbnail creation for all tests."""
    monkeypatch.setattr('sonar.modules.utils.Image.make_blob', lambda *args:
                        b'Fake thumbnail image content')
