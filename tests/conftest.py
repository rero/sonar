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
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Common pytest fixtures and plugins."""

import copy
import os
import tempfile
from io import BytesIO

import pytest
from flask_principal import ActionNeed
from invenio_access.models import ActionUsers, Role
from invenio_accounts.ext import hash_password
from invenio_files_rest.models import Location
from utils import MockArkServer

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.deposits.api import DepositRecord
from sonar.modules.documents.api import DocumentRecord
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.users.api import UserRecord
from sonar.proxies import sonar


@pytest.fixture(scope='function')
def mock_ark(app, monkeypatch):
    """Mock for the ARK module."""
    # be sure that we do not make any request on the ARK server
    monkeypatch.setattr(
        'requests.get', lambda *args, **kwargs: MockArkServer.get(
            *args, **kwargs))
    monkeypatch.setattr(
        'requests.post', lambda *args, **kwargs: MockArkServer.post(
            *args, **kwargs))
    monkeypatch.setattr(
        'requests.put', lambda *args, **kwargs: MockArkServer.put(
            *args, **kwargs))
    # enable ARK
    monkeypatch.setitem(app.config, 'SONAR_APP_ARK_NMA',
                        'https://www.arketype.ch')


@pytest.fixture(scope='module')
def es(appctx):
    """Setup and teardown all registered Elasticsearch indices.

    Scope: module
    This fixture will create all registered indexes in Elasticsearch and remove
    once done. Fixtures that perform changes (e.g. index or remove documents),
    should used the function-scoped :py:data:`es_clear` fixture to leave the
    indexes clean for the following tests.
    """
    from invenio_search import current_search, current_search_client
    from invenio_search.errors import IndexAlreadyExistsError

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

    # ARK
    app_config['SONAR_APP_ARK_USER'] = 'test'
    app_config['SONAR_APP_ARK_PASSWORD'] = 'test'
    app_config['SONAR_APP_ARK_RESOLVER'] = 'https://n2t.net'
    # ARK is disabled by default
    app_config['SONAR_APP_ARK_NMA'] = None
    app_config['SONAR_APP_ARK_NAAN'] = '99999'
    app_config['SONAR_APP_ARK_SCHEME'] = 'ark:'
    app_config['SONAR_APP_ARK_SHOULDER'] = 'ffk3'
    return app_config


@pytest.fixture
def make_organisation(app, db, bucket_location, without_oaiset_signals):
    """Factory for creating organisation."""

    def _make_organisation(code):
        data = {
            'code': code,
            'name': code,
            'isShared': True,
            'isDedicated': False,
            'documentsCustomField1': {
                'label': [{
                    'language': 'eng',
                    'value': 'Test'
                }],
                'includeInFacets': True
            }
        }

        record = OrganisationRecord.get_record_by_pid(code)

        if not record:
            record = OrganisationRecord.create(data, dbcommit=True)
            record.reindex()
            db.session.commit()

        return record

    return _make_organisation


@pytest.fixture()
def organisation(make_organisation):
    """Create an organisation."""
    return make_organisation('org')


@pytest.fixture()
def roles(base_app, db):
    """Create user roles."""
    datastore = base_app.extensions['invenio-accounts'].datastore

    for role in UserRecord.available_roles:
        db_role = datastore.find_role(role)

        if not db_role:
            datastore.create_role(name=role)

        datastore.commit()

    db.session.commit()


@pytest.fixture
def make_user(app, db, make_organisation):
    """Factory for creating user."""

    def _make_user(role_name, organisation='org', access=None):
        name = role_name

        if organisation:
            make_organisation(organisation)
            name = organisation + name

        email = '{name}@rero.ch'.format(name=name)

        datastore = app.extensions['security'].datastore

        user = datastore.find_user(email=email)

        if user:
            record = UserRecord.get_user_by_email(email)
            return record

        user = datastore.create_user(email=email,
                                     password=hash_password('123456'),
                                     active=True)
        datastore.commit()

        role = datastore.find_role(role_name)
        if not role:
            role = Role(name=role_name)

        role.users.append(user)

        db.session.add(role)

        if access:
            db.session.add(ActionUsers.allow(ActionNeed(access), user=user))

        db.session.commit()

        data = {
            'pid': name,
            'email': email,
            'first_name': name[0].upper() + name[1:],
            'last_name': 'Doe',
            'role': role_name
        }

        if organisation:
            data['organisation'] = {
                '$ref':
                'https://sonar.ch/api/organisations/{organisation}'.format(
                    organisation=organisation)
            }

        record = UserRecord.create(data, dbcommit=True)
        record.reindex()
        db.session.commit()

        return record

    return _make_user


@pytest.fixture()
def user_without_role(app, db):
    """Create user in database without role."""
    datastore = app.extensions['security'].datastore
    user = datastore.create_user(email='user-without-role@rero.ch',
                                 password=hash_password('123456'),
                                 active=True)
    db.session.commit()

    return user


@pytest.fixture()
def user(make_user):
    """Create user."""
    return make_user('user')


@pytest.fixture()
def moderator(make_user):
    """Create moderator."""
    return make_user('moderator', access='admin-access')


@pytest.fixture()
def submitter(make_user):
    """Create submitter."""
    return make_user('submitter', access='admin-access')


@pytest.fixture()
def admin(make_user):
    """Create admin user."""
    return make_user('admin', access='admin-access')


@pytest.fixture()
def superuser(make_user):
    """Create super user."""
    return make_user('superuser', access='superuser-access')


@pytest.fixture()
def document_json(app, db, bucket_location, organisation):
    """JSON document fixture."""
    data = {
        'identifiedBy': [{
            'value': 'urn:nbn:ch:rero-006-108713',
            'type': 'bf:Urn'
        }, {
            'value': 'oai:doc.rero.ch:20050302172954-WU',
            'type': 'bf:Identifier'
        }, {
            'value': '111111',
            'type': 'bf:Local',
            'source': 'RERO DOC'
        }, {
            'value': 'R003415713',
            'type': 'bf:Local',
            'source': 'RERO'
        }],
        'language': [{
            'value': 'eng',
            'type': 'bf:Language'
        }],
        'contribution': [{
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'John, Doe',
                'date_of_birth': '1960',
                'date_of_death': '2000'
            },
            'role': ['cre'],
            'affiliation': 'Institute for Research'
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
        }, {
            'language': 'fre',
            'value': 'Résumé'
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
        'partOf': [{
            'document': {
                'contribution': ['Renato, Ferrari', 'Albano, Mesta'],
                'publication': {
                    'startDate': '2019-05-05',
                    'statement': 'John Doe Publications inc.'
                },
                'title': 'Journal du dimanche'
            },
            'numberingPages': '135-139',
            'numberingYear': '2020',
            'numberingVolume': '6',
            'numberingIssue': '12'
        }],
        'editionStatement': {
            'editionDesignation': {
                'value': 'Di 3 ban'
            },
            'responsibility': {
                'value': 'Zeng Lingliang zhu bian'
            }
        },
        'dissertation': {
            'degree': 'Doctoral thesis',
            'grantingInstitution': 'Università della Svizzera italiana',
            'date': '2010-12-01',
            'jury_note': 'Jury note'
        },
        'customField1': ['Test']
    }

    return data


@pytest.fixture()
def make_document(db, document_json, make_organisation, pdf_file):
    """Factory for creating document."""

    def _make_document(organisation='org', with_file=False, pid=None):
        if organisation:
            make_organisation(organisation)
            document_json['organisation'] = [{
                '$ref':
                'https://sonar.ch/api/organisations/org'
            }]

        if pid:
            document_json['pid'] = pid
        else:
            document_json.pop('pid', None)
            document_json.pop('_oai', None)

        record = DocumentRecord.create(document_json,
                                       dbcommit=True,
                                       with_bucket=True)
        record.commit()
        db.session.commit()

        if with_file:
            with open(pdf_file, 'rb') as file:
                record.add_file(file.read(),
                                'test1.pdf',
                                order=1,
                                access='coar:c_f1cf',
                                restricted_outside_organisation=False,
                                embargo_date='2022-01-01')
                record.commit()

        db.session.commit()
        record.reindex()
        return record

    return _make_document


@pytest.fixture()
def document(make_document):
    """Create a document."""
    return make_document('org', False)


@pytest.fixture()
def document_with_file(make_document):
    """Create a document with a file associated."""
    return make_document('org', True)


@pytest.fixture()
def deposit_json(collection, subdivision):
    """Deposit JSON."""
    return {
        '$schema':
        'https://sonar.ch/schemas/deposits/deposit-v1.0.0.json',
        '_bucket':
        '03e5e909-2fce-479e-a697-657e1392cc72',
        'contributors': [{
            'affiliation': 'University of Bern, Switzerland',
            'name': 'Takayoshi, Shintaro',
            'role': 'cre',
            'orcid': '1234-5678-1234-5678'
        }],
        'metadata': {
            'documentType':
            'coar:c_816b',
            'title':
            'Title of the document',
            'subtitle':
            'Subtitle of the document',
            'otherLanguageTitle': {
                'language': 'fre',
                'title': 'Titre du document'
            },
            'language':
            'eng',
            'publicationPlace':
            'Place',
            'publisher':
            'Publisher name',
            'documentDate':
            '2020',
            'publication': {
                'publishedIn': 'Journal',
                'volume': '12',
                'number': '2',
                'pages': '1-12',
                'editors': ['Denson, Edward', 'Worth, James'],
                'publisher': 'Publisher'
            },
            'otherElectronicVersions': [{
                'publicNote': 'Published version',
                'url': 'https://some.url/document.pdf'
            }],
            'collections': [{
                '$ref':
                f'https://sonar.ch/api/collections/{collection["pid"]}'
            }, {
                'name': [{
                    'language': 'eng',
                    'value': 'New collection'
                }]
            }],
            'classification':
            '543',
            'abstracts': [{
                'language': 'eng',
                'abstract': 'Abstract of the document'
            }, {
                'language': 'fre',
                'abstract': 'Résumé du document'
            }],
            'subjects': [{
                'language': 'eng',
                'subjects': ['Subject 1', 'Subject 2']
            }, {
                'language': 'fre',
                'subjects': ['Sujet 1', 'Sujet 2']
            }],
            'dissertation': {
                'degree': 'Doctoral thesis',
                'grantingInstitution': 'Università della Svizzera italiana',
                'date': '2010-12-01',
                'jury_note': 'Jury note'
            },
            'identifiedBy': [{
                'type': 'pmid',
                'value': '123456'
            }, {
                'type': 'bf:Local',
                'value': '9999',
                'source': 'RERO'
            }, {
                'type': 'bf:Doi',
                'value': '10.1038/nphys1170'
            }]
        },
        'diffusion': {
            'license':
            'CC0',
            'oa_status':
            'green',
            'subdivisions': [{
                '$ref':
                f'https://sonar.ch/api/subdivisions/{subdivision["pid"]}'
            }],
        },
        'status':
        'in_progress',
        'step':
        'diffusion'
    }


@pytest.fixture()
def make_deposit(db, deposit_json, bucket_location, pdf_file, make_user):
    """Factory for creating deposit."""

    def _make_deposit(role='submitter', organisation=None):
        user = make_user(role, organisation)

        deposit_json['user'] = {
            '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=user['pid'])
        }

        deposit_json.pop('pid', None)

        record = DepositRecord.create(deposit_json,
                                      dbcommit=True,
                                      with_bucket=True)

        with open(pdf_file, 'rb') as file:
            content = file.read()

        record.files['main.pdf'] = BytesIO(content)
        record.files['main.pdf']['label'] = 'Main file'
        record.files['main.pdf']['category'] = 'main'
        record.files['main.pdf']['type'] = 'file'
        record.files['main.pdf']['embargo'] = True
        record.files['main.pdf']['embargoDate'] = '2022-01-01'
        record.files['main.pdf']['exceptInOrganisation'] = True

        record.files['additional.pdf'] = BytesIO(content)
        record.files['additional.pdf']['label'] = 'Additional file 1'
        record.files['additional.pdf']['category'] = 'additional'
        record.files['additional.pdf']['type'] = 'file'
        record.files['additional.pdf']['embargo'] = False
        record.files['additional.pdf']['exceptInOrganisation'] = False

        record.commit()
        record.reindex()
        db.session.commit()

        return record

    return _make_deposit


@pytest.fixture()
def deposit(app, db, user, pdf_file, bucket_location, deposit_json):
    """Deposit fixture."""
    json = copy.deepcopy(deposit_json)
    json['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=user['pid'])
    }

    deposit = DepositRecord.create(json, dbcommit=True, with_bucket=True)

    with open(pdf_file, 'rb') as file:
        content = file.read()

    deposit.files['main.pdf'] = BytesIO(content)
    deposit.files['main.pdf']['label'] = 'Main file'
    deposit.files['main.pdf']['category'] = 'main'
    deposit.files['main.pdf']['type'] = 'file'
    deposit.files['main.pdf']['embargo'] = True
    deposit.files['main.pdf']['embargoDate'] = '2022-01-01'
    deposit.files['main.pdf']['exceptInOrganisation'] = True

    deposit.files['additional.pdf'] = BytesIO(content)
    deposit.files['additional.pdf']['label'] = 'Additional file 1'
    deposit.files['additional.pdf']['category'] = 'additional'
    deposit.files['additional.pdf']['type'] = 'file'
    deposit.files['additional.pdf']['embargo'] = False
    deposit.files['additional.pdf']['exceptInOrganisation'] = False

    deposit.commit()
    deposit.reindex()
    db.session.commit()

    return deposit


@pytest.fixture()
def project_json():
    """Project JSON."""
    return {
        'metadata': {
            'name':
            'Project 1',
            'description':
            'Description of the project',
            'startDate':
            '2019-01-01',
            'endDate':
            '2020-01-01',
            'identifiedBy': {
                'type': 'bf:Local',
                'source': 'RERO',
                'value': '1111'
            },
            'investigators': [{
                'agent': {
                    'preferred_name': 'John Doe'
                },
                'role': ['investigator'],
                'affiliation': 'IST',
                'identifiedBy': {
                    'type': 'bf:Local',
                    'source': 'RERO',
                    'value': '2222'
                }
            }],
            'funding_organisations': [{
                'agent': {
                    'preferred_name': 'Funding organisation'
                },
                'identifiedBy': {
                    'type': 'bf:Local',
                    'source': 'RERO',
                    'value': '3333'
                }
            }],
            'validation': {
                'user': {
                    '$ref': 'https://sonar.ch/api/users/orgsubmitter'
                },
                'status': 'validated',
                'action': 'save'
            }
        }
    }


@pytest.fixture()
def make_project(app, db, project_json, make_user):
    """Factory for creating project."""

    def _make_project(role='submitter', organisation=None):
        user = make_user(role, organisation)

        project_json['metadata']['user'] = {
            '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=user['pid'])
        }

        project_json['metadata']['organisation'] = {
            '$ref':
            'https://sonar.ch/api/organisations/{pid}'.format(pid=organisation)
        }

        project_json.pop('id', None)

        project = sonar.service('projects').create(None, project_json)
        app.extensions['invenio-search'].flush_and_refresh(index='projects')
        return project

    return _make_project


@pytest.fixture()
def project(app, db, es, admin, organisation, project_json):
    """Deposit fixture."""
    json = copy.deepcopy(project_json)
    json['metadata']['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=admin['pid'])
    }
    json['metadata']['organisation'] = {
        '$ref':
        'https://sonar.ch/api/organisations/{pid}'.format(
            pid=organisation['pid'])
    }

    project = sonar.service('projects').create(None, json)
    app.extensions['invenio-search'].flush_and_refresh(index='projects')
    return project


@pytest.fixture()
def collection_json():
    """Collection JSON."""
    return {
        'name': [{
            'language': 'eng',
            'value': 'Collection name'
        }],
        'description': [{
            'language': 'eng',
            'value': 'Collection description'
        }]
    }


@pytest.fixture()
def make_collection(app, db, collection_json):
    """Factory for creating collection."""

    def _make_collection(organisation=None):
        collection_json['organisation'] = {
            '$ref':
            'https://sonar.ch/api/organisations/{pid}'.format(pid=organisation)
        }

        collection_json.pop('pid', None)

        collection = CollectionRecord.create(collection_json,
                                             dbcommit=True,
                                             with_bucket=True)
        collection.commit()
        collection.reindex()
        db.session.commit()
        return collection

    return _make_collection


@pytest.fixture()
def collection(app, db, es, admin, organisation, collection_json):
    """Collection fixture."""
    json = copy.deepcopy(collection_json)
    json['organisation'] = {
        '$ref':
        'https://sonar.ch/api/organisations/{pid}'.format(
            pid=organisation['pid'])
    }

    collection = CollectionRecord.create(json, dbcommit=True, with_bucket=True)
    collection.commit()
    collection.reindex()
    db.session.commit()
    return collection


@pytest.fixture()
def subdivision_json():
    """Subdivision JSON."""
    return {'name': [{'language': 'eng', 'value': 'Subdivision name'}]}


@pytest.fixture()
def make_subdivision(app, db, subdivision_json):
    """Factory for creating subdivision."""

    def _make_subdivision(organisation=None):
        subdivision_json['organisation'] = {
            '$ref':
            'https://sonar.ch/api/organisations/{pid}'.format(pid=organisation)
        }

        subdivision_json.pop('pid', None)

        subdivision = SubdivisionRecord.create(subdivision_json, dbcommit=True)
        subdivision.commit()
        subdivision.reindex()
        db.session.commit()
        return subdivision

    return _make_subdivision


@pytest.fixture()
def subdivision(app, db, es, admin, organisation, subdivision_json):
    """Subdivision fixture."""
    json = copy.deepcopy(subdivision_json)
    json['organisation'] = {
        '$ref':
        'https://sonar.ch/api/organisations/{pid}'.format(
            pid=organisation['pid'])
    }

    subdivision = SubdivisionRecord.create(json, dbcommit=True)
    subdivision.commit()
    subdivision.reindex()
    db.session.commit()
    return subdivision


@pytest.fixture()
def bucket_location(app, db):
    """Create a default location for managing files."""
    tmppath = tempfile.mkdtemp()
    location = Location(name='default', uri=tmppath, default=True)
    db.session.add(location)
    db.session.commit()
    return location


@pytest.fixture()
def pdf_file():
    """Return test PDF file path."""
    return os.path.dirname(os.path.abspath(__file__)) + '/data/test.pdf'


@pytest.fixture(autouse=True)
def mock_thumbnail_creation(monkeypatch):
    """Mock thumbnail creation for all tests."""
    monkeypatch.setattr('sonar.modules.utils.Image.make_blob', lambda *args:
                        b'Fake thumbnail image content')


@pytest.yield_fixture
def without_oaiset_signals(app):
    """Temporary disable oaiset signals."""
    from invenio_oaiserver import current_oaiserver
    current_oaiserver.unregister_signals_oaiset()
    yield
    current_oaiserver.register_signals_oaiset()
