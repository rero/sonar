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

import copy
import os
import tempfile
from io import BytesIO

import pytest
from flask_principal import ActionNeed
from invenio_access.models import ActionUsers, Role
from invenio_accounts.ext import hash_password
from invenio_files_rest.models import Location

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.documents.api import DocumentRecord
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.projects.api import ProjectRecord
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

    return app_config


@pytest.fixture
def make_organisation(app, db, bucket_location, without_oaiset_signals):
    """Factory for creating organisation."""

    def _make_organisation(code):
        data = {
            'code': code,
            'name': code,
            'isShared': True,
            'isDedicated': False
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

    def _make_user(role_name, organisation='org'):
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
        db.session.add(
            ActionUsers.allow(ActionNeed(
                '{role}-access'.format(role=role_name)),
                              user=user))
        db.session.commit()

        data = {
            'pid': name,
            'email': email,
            'full_name': name,
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
    return make_user('moderator')


@pytest.fixture()
def submitter(make_user):
    """Create submitter."""
    return make_user('submitter')


@pytest.fixture()
def admin(make_user):
    """Create admin user."""
    return make_user('admin')


@pytest.fixture()
def superuser(make_user):
    """Create super user."""
    return make_user('superuser')


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
            'type': 'bf:Local'
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
        }
    }

    return data


@pytest.fixture()
def make_document(db, document_json, make_organisation, pdf_file):
    """Factory for creating document."""

    def _make_document(organisation='org', with_file=False, pid=None):
        if organisation:
            make_organisation(organisation)
            document_json['organisation'] = {
                '$ref': 'https://sonar.ch/api/organisations/org'
            }

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
                                embargo_date='2021-01-01')
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
def deposit_json():
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
            'documentDate':
            '2020-01-01',
            'publication': {
                'publishedIn': 'Journal',
                'year': '2019',
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
            'specificCollections': ['Collection 1', 'Collection 2'],
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
            'license': 'CC0'
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
        record.files['main.pdf']['embargoDate'] = '2021-01-01'
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
    deposit.files['main.pdf']['embargoDate'] = '2021-01-01'
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
        '$schema':
        'https://sonar.ch/schemas/projects/project-v1.0.0.json',
        'pid':
        '11111',
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
        }]
    }


@pytest.fixture()
def make_project(db, project_json, make_user):
    """Factory for creating project."""

    def _make_project(role='submitter', organisation=None):
        user = make_user(role, organisation)

        project_json['user'] = {
            '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=user['pid'])
        }

        project_json['organisation'] = {
            '$ref':
            'https://sonar.ch/api/organisations/{pid}'.format(pid=organisation)
        }

        project_json.pop('pid', None)

        record = ProjectRecord.create(project_json,
                                      dbcommit=True,
                                      with_bucket=False)
        record.commit()
        record.reindex()
        db.session.commit()

        return record

    return _make_project


@pytest.fixture()
def project(app, db, user, organisation, project_json):
    """Deposit fixture."""
    json = copy.deepcopy(project_json)
    json['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=user['pid'])
    }
    json['organisation'] = {
        '$ref':
        'https://sonar.ch/api/organisations/{pid}'.format(
            pid=organisation['pid'])
    }

    project = ProjectRecord.create(json, dbcommit=True, with_bucket=False)
    project.commit()
    project.reindex()
    db.session.commit()

    return project


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
