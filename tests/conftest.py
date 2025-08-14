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
import shutil
import sys
import tempfile
from datetime import date
from io import BytesIO
from os.path import dirname, join

import mock
import pytest
import requests_mock
from dotenv import load_dotenv
from flask_principal import ActionNeed
from flask_security.utils import hash_password
from invenio_access.models import ActionUsers, Role
from invenio_db import db as db_
from invenio_files_rest.models import Location
from invenio_queues.proxies import current_queues
from sqlalchemy_utils import create_database, database_exists

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.deposits.api import DepositRecord
from sonar.modules.documents.api import DocumentRecord
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.users.api import UserRecord
from sonar.proxies import sonar


# # Needed if tests working with SQLite
@pytest.fixture()
def db(app):
    """Get setup database."""
    if not database_exists(str(db_.engine.url.render_as_string(hide_password=False))):
        create_database(str(db_.engine.url.render_as_string(hide_password=False)))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()
    # drop_alembic_version_table()


@pytest.fixture()
def event_queues(app):
    """Delete and declare test queues."""
    current_queues.delete()
    try:
        current_queues.declare()
        yield
    finally:
        current_queues.delete()


@pytest.fixture(scope="module")
def embargo_date():
    """Embargo date in one year from now."""
    today = date.today()
    return today.replace(year=today.year + 1)


@pytest.fixture(scope="module")
def search(appctx):
    """Setup and teardown all registered Elasticsearch indices.

    Scope: module
    This fixture will create all registered indexes in Elasticsearch and remove
    once done. Fixtures that perform changes (e.g. index or remove documents),
    should used the function-scoped :py:data:`search_clear` fixture to leave the
    indexes clean for the following tests.
    """
    from invenio_search import current_search, current_search_client
    from invenio_search.errors import IndexAlreadyExistsError

    try:
        list(current_search.put_templates())
    except IndexAlreadyExistsError:
        current_search_client.indices.delete_template("*")
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
        current_search_client.indices.delete(index="*")
        current_search_client.indices.delete_template("*")


@pytest.fixture(scope="module")
def instance_path():
    """Temporary instance path.

    Scope: module

    This fixture creates a temporary directory if the
    environment variable ``INVENIO_INSTANCE_PATH`` is not be set.
    This directory is then automatically removed.
    """
    # load .env, .flaskenv
    load_dotenv()
    invenio_instance_path = os.environ.get("INVENIO_INSTANCE_PATH")
    invenio_static_folder = os.environ.get("INVENIO_STATIC_FOLDER")
    path = invenio_instance_path
    # static folder
    if not invenio_static_folder:
        if invenio_instance_path:
            os.environ["INVENIO_STATIC_FOLDER"] = os.path.join(
                invenio_instance_path, "static"
            )
        else:
            os.environ["INVENIO_STATIC_FOLDER"] = os.path.join(
                sys.prefix, "var/instance/static"
            )
    # instance path
    if not path:
        path = tempfile.mkdtemp()
        os.environ["INVENIO_INSTANCE_PATH"] = path
    yield path
    # clean static folder variable
    if not invenio_static_folder:
        os.environ.pop("INVENIO_STATIC_FOLDER", None)
    # clean instance path variable and remove temp dir
    if not invenio_instance_path:
        os.environ.pop("INVENIO_INSTANCE_PATH", None)
        shutil.rmtree(path)


@pytest.fixture(scope="module", autouse=True)
def app_config(app_config):
    """Define configuration for module."""
    help_test_dir = join(dirname(__file__), "data", "help")

    app_config["SHIBBOLETH_SERVICE_PROVIDER"] = dict(
        strict=True,
        debug=True,
        entity_id="entity_id",
        x509cert="./docker/nginx/sp.pem",
        private_key="./docker/nginx/sp.key",
    )

    app_config["SHIBBOLETH_IDENTITY_PROVIDERS"] = dict(
        idp=dict(
            entity_id="https://idp.com/shibboleth",
            sso_url="https://idp.com/Redirect/SSO",
            mappings=dict(
                email="email",
                full_name="name",
                user_unique_id="id",
            ),
        )
    )

    # ARK
    app_config["SONAR_APP_ARK_RESOLVER"] = "https://n2t.net"
    # ARK is disabled by default
    app_config["SONAR_APP_ARK_NAAN"] = "99999"
    app_config["SONAR_APP_ARK_SCHEME"] = "ark:"
    app_config["SONAR_APP_ARK_SHOULDER"] = "ffk3"

    # Celery
    app_config["CACHE_TYPE"] = "simple"
    app_config["CELERY_BROKER_URL"] = "memory://"
    app_config["CELERY_CACHE_BACKEND"] = "memory"
    app_config["CELERY_RESULT_BACKEND"] = "cache"
    app_config["CELERY_TASK_ALWAYS_EAGER"] = True
    app_config["CELERY_TASK_EAGER_PROPAGATES"] = True
    app_config["CELERY_REDIS_SCHEDULER_URL"] = "redis://localhost:6379/4"

    # Other configs
    app_config["ACCOUNTS_SESSION_REDIS_URL"] = "redis://localhost:6379/1"
    app_config["CACHE_REDIS_URL"] = "redis://cache:6379/0"
    app_config["CELERY_REDIS_SCHEDULER_URL"] = "redis://localhost:6379/4"
    app_config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
    app_config["PDF_EXTRACTOR_GROBID_PORT"] = "8070"
    app_config["RATELIMIT_STORAGE_URI"] = "redis://localhost:6379/3"
    app_config["SEARCH_ELASTIC_HOSTS"] = ["localhost:9200"]
    app_config["SONAR_APP_DEFAULT_ORGANISATION"] = "global"
    app_config["SONAR_APP_SERVER_NAME"] = "sonar.rero.ch"
    app_config["SONAR_APP_URN_DNB_BASE_URL"] = (
        "https://api.nbn-resolving.org/sandbox/v2"
    )
    app_config["SONAR_APP_URN_DNB_BASE_URN"] = "urn:nbn:ch:rero-"
    app_config["SONAR_APP_URN_DNB_PASSWORD"] = ""
    app_config["SONAR_APP_URN_DNB_USERNAME"] = ""
    app_config["WIKI_CONTENT_DIR"] = help_test_dir
    app_config["WIKI_UPLOAD_FOLDER"] = join(help_test_dir, "files")
    app_config["WTF_CSRF_ENABLED"] = False
    app_config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg2://sonar:sonar@localhost/sonar"
    )
    # org.domain.com needed for sitemap tests
    app_config["TRUSTED_HOSTS"] = [
        "sonar.ch",
        "sonar.rero.ch",
        "localhost",
        "127.0.0.1",
        "org.domain.com",
    ]
    app_config
    return app_config


@pytest.fixture
def make_organisation(app, db, bucket_location, without_oaiset_signals):
    """Factory for creating organisation."""

    def _make_organisation(code, is_shared=True):
        data = {
            "code": code,
            "name": code,
            "isShared": is_shared,
            "arkNAAN": "99999",
            "isDedicated": not is_shared,
            "documentsCustomField1": {
                "label": [{"language": "eng", "value": "Test"}],
                "includeInFacets": True,
            },
        }

        record = OrganisationRecord.get_record_by_pid(code)

        if not record:
            record = OrganisationRecord.create(data, dbcommit=True)
            db.session.commit()
        record.reindex()

        return record

    return _make_organisation


@pytest.fixture()
def organisation(make_organisation):
    """Create an organisation."""
    return make_organisation("org")


@pytest.fixture()
def organisation_with_urn(app, make_organisation):
    """Create an organisation."""
    app.config["SONAR_APP_DOCUMENT_URN"] = {
        "organisations": {"org": {"types": ["coar:c_db06"], "code": 6}}
    }
    return make_organisation("org")


@pytest.fixture()
def organisation_with_file(organisation, pdf_file):
    """Create an organisation with a file attached."""
    with open(pdf_file, "rb") as file:
        organisation.add_file(file.read(), "test1.pdf")
        organisation.commit()
    return organisation


@pytest.fixture()
def roles(base_app, db):
    """Create user roles."""
    datastore = base_app.extensions["invenio-accounts"].datastore

    for role in UserRecord.available_roles:
        db_role = datastore.find_role(role)

        if not db_role:
            datastore.create_role(name=role)

        datastore.commit()

    db.session.commit()


@pytest.fixture
def make_user(app, db, make_organisation, roles):
    """Factory for creating user."""

    def _make_user(
        role_name, organisation="org", organisation_is_shared=True, access=None
    ):
        name = role_name

        if organisation:
            make_organisation(organisation, is_shared=organisation_is_shared)
            name = organisation + name

        email = f"{name}@rero.ch"

        datastore = app.extensions["security"].datastore

        if record := UserRecord.get_user_by_email(email):
            return record

        user = datastore.create_user(
            email=email, password=hash_password("123456"), active=True
        )
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
            "pid": name,
            "email": email,
            "first_name": name[0].upper() + name[1:],
            "last_name": "Doe",
            "role": role_name,
        }

        if organisation:
            data["organisation"] = {
                "$ref": f"https://sonar.ch/api/organisations/{organisation}"
            }

        record = UserRecord.create(data, dbcommit=True)
        record.reindex()
        db.session.commit()

        return record

    return _make_user


@pytest.fixture()
def user_without_role(app, db):
    """Create user in database without role."""
    datastore = app.extensions["security"].datastore
    user = datastore.create_user(
        email="user-without-role@rero.ch", password=hash_password("123456"), active=True
    )
    db.session.commit()

    return user


@pytest.fixture()
def user_without_org(make_user):
    """Create user without organisation."""
    return make_user("user", None)


@pytest.fixture()
def user(make_user):
    """Create user."""
    return make_user("user")


@pytest.fixture()
def moderator(make_user):
    """Create moderator."""
    return make_user("moderator", access="admin-access")


@pytest.fixture()
def moderator_dedicated(make_user):
    """Create moderator organisation dedicated."""
    return make_user(
        "moderator",
        organisation="dedicated",
        organisation_is_shared=False,
        access="admin-access",
    )


@pytest.fixture()
def submitter(make_user):
    """Create submitter."""
    return make_user("submitter", access="admin-access")


@pytest.fixture()
def admin(make_user):
    """Create admin user."""
    return make_user("admin", access="admin-access")


@pytest.fixture()
def admin_shared(make_user):
    """Create shared admin user."""
    return make_user(
        "admin",
        organisation="shared",
        organisation_is_shared=True,
        access="admin-access",
    )


@pytest.fixture()
def superuser(make_user):
    """Create super user."""
    return make_user("superuser", access="superuser-access")


@pytest.fixture()
def document_json(app, db, bucket_location, organisation):
    """JSON document fixture."""
    return {
        "identifiedBy": [
            {"value": "oai:doc.rero.ch:20050302172954-WU", "type": "bf:Identifier"},
            {"value": "111111", "type": "bf:Local", "source": "RERO DOC"},
            {"value": "R003415713", "type": "bf:Local", "source": "RERO"},
        ],
        "language": [{"value": "eng", "type": "bf:Language"}],
        "contribution": [
            {
                "agent": {
                    "type": "bf:Person",
                    "preferred_name": "John, Doe",
                    "date_of_birth": "1960",
                    "date_of_death": "2000",
                },
                "role": ["cre"],
                "affiliation": "Institute for Research",
            }
        ],
        "title": [
            {
                "type": "bf:Title",
                "mainTitle": [{"language": "eng", "value": "Title of the document"}],
            }
        ],
        "extent": "103 p",
        "abstracts": [
            {"language": "eng", "value": "Abstract of the document"},
            {"language": "fre", "value": "Résumé"},
        ],
        "subjects": [
            {
                "label": {
                    "language": "eng",
                    "value": ["Time series models", "GARCH models"],
                },
                "source": "RERO",
            }
        ],
        "provisionActivity": [
            {
                "type": "bf:Manufacture",
                "statement": [
                    {"label": [{"value": "Bienne"}], "type": "bf:Place"},
                    {"label": [{"value": "Impr. Weber"}], "type": "bf:Agent"},
                    {"label": [{"value": "[2006]"}], "type": "Date"},
                    {"label": [{"value": "Lausanne"}], "type": "bf:Place"},
                    {"label": [{"value": "Rippone"}], "type": "bf:Place"},
                    {"label": [{"value": "Impr. Coustaud"}], "type": "bf:Agent"},
                ],
            }
        ],
        "partOf": [
            {
                "document": {
                    "contribution": ["Renato, Ferrari", "Albano, Mesta"],
                    "publication": {
                        "startDate": "2019-05-05",
                        "statement": "John Doe Publications inc.",
                    },
                    "title": "Journal du dimanche",
                },
                "numberingPages": "135-139",
                "numberingYear": "2020",
                "numberingVolume": "6",
                "numberingIssue": "12",
            }
        ],
        "editionStatement": {
            "editionDesignation": {"value": "Di 3 ban"},
            "responsibility": {"value": "Zeng Lingliang zhu bian"},
        },
        "dissertation": {
            "degree": "Doctoral thesis",
            "grantingInstitution": "Università della Svizzera italiana",
            "date": "2010-12-01",
            "jury_note": "Jury note",
        },
        "customField1": ["Test"],
    }


@pytest.fixture()
def make_document(db, document_json, make_organisation, pdf_file, embargo_date):
    """Factory for creating document."""

    def _make_document(
        data=document_json, organisation="org", with_file=False, pid=None
    ):
        if organisation:
            make_organisation(organisation)
            data["organisation"] = [{"$ref": "https://sonar.ch/api/organisations/org"}]

        if pid:
            data["pid"] = pid
        else:
            data.pop("pid", None)
            data.pop("_oai", None)

        record = DocumentRecord.create(document_json, dbcommit=True, with_bucket=True)
        record.commit()
        db.session.commit()

        if with_file:
            with open(pdf_file, "rb") as file:
                record.add_file(
                    file.read(),
                    "test1.pdf",
                    order=1,
                    access="coar:c_f1cf",
                    restricted_outside_organisation=False,
                    embargo_date=embargo_date.isoformat(),
                )
                record.commit()

        db.session.commit()
        record.reindex()
        return record

    return _make_document


@pytest.fixture(scope="function")
def document(make_document):
    """Create a document."""
    return make_document(organisation="org", with_file=False)


@pytest.fixture()
def document_with_file(make_document):
    """Create a document with a file associated."""
    return make_document(organisation="org", with_file=True)


@pytest.fixture()
def deposit_json(collection, subdivision):
    """Deposit JSON."""
    return {
        "$schema": "https://sonar.ch/schemas/deposits/deposit-v1.0.0.json",
        "_bucket": "03e5e909-2fce-479e-a697-657e1392cc72",
        "contributors": [
            {
                "affiliation": "University of Bern, Switzerland",
                "name": "Takayoshi, Shintaro",
                "role": "cre",
                "orcid": "1234-5678-1234-5678",
            }
        ],
        "metadata": {
            "documentType": "coar:c_816b",
            "title": "Title of the document",
            "subtitle": "Subtitle of the document",
            "otherLanguageTitle": {"language": "fre", "title": "Titre du document"},
            "language": "eng",
            "publicationPlace": "Place",
            "publisher": "Publisher name",
            "documentDate": "2020",
            "statementDate": "2019",
            "publication": {
                "publishedIn": "Journal",
                "volume": "12",
                "number": "2",
                "pages": "1-12",
                "editors": ["Denson, Edward", "Worth, James"],
                "publisher": "Publisher",
                "identifiedBy": [
                    {"type": "bf:Isbn", "value": "ISBN"},
                    {"type": "bf:Issn", "value": "ISSN"},
                ],
            },
            "otherElectronicVersions": [
                {
                    "publicNote": "Published version",
                    "url": "https://some.url/document.pdf",
                }
            ],
            "relatedTo": [
                {
                    "publicNote": "Related to version",
                    "url": "https://some.url/related.pdf",
                }
            ],
            "collections": [
                {"$ref": f'https://sonar.ch/api/collections/{collection["pid"]}'}
            ],
            "classification": "543",
            "abstracts": [
                {"language": "eng", "abstract": "Abstract of the document"},
                {"language": "fre", "abstract": "Résumé du document"},
            ],
            "subjects": [
                {"language": "eng", "subjects": ["Subject 1", "Subject 2"]},
                {"language": "fre", "subjects": ["Sujet 1", "Sujet 2"]},
            ],
            "dissertation": {
                "degree": "Doctoral thesis",
                "grantingInstitution": "Università della Svizzera italiana",
                "date": "2010-12-01",
                "jury_note": "Jury note",
            },
            "identifiedBy": [
                {"type": "pmid", "value": "123456"},
                {"type": "bf:Local", "value": "9999", "source": "RERO"},
                {"type": "bf:Doi", "value": "10.1038/nphys1170"},
            ],
            "contentNote": ["Note 1", "Note 2"],
            "extent": "Extent value",
            "additionalMaterials": "Additional materials",
            "formats": ["Format 1", "Format 2"],
            "otherMaterialCharacteristics": "Other material characteristics",
            "editionStatement": {
                "editionDesignation": {"value": "1st edition"},
                "responsibility": {"value": "Resp."},
            },
            "notes": ["Note 1", "Note 2"],
            "series": [{"name": "Serie 1", "number": "12"}, {"name": "Serie 2"}],
            "partOf": [
                {
                    "document": {
                        "contribution": ["Renato, Ferrari", "Albano, Mesta"],
                        "title": "Journal du dimanche",
                        "identifiedBy": [
                            {"type": "bf:Isbn", "value": "958710532X"},
                            {"type": "bf:Issn", "value": "958710532X"},
                        ],
                    },
                    "numberingPages": "135-139",
                    "numberingYear": "2020",
                    "numberingVolume": "6",
                    "numberingIssue": "12",
                }
            ],
        },
        "diffusion": {
            "license": "CC0",
            "oa_status": "green",
            "subdivisions": [
                {"$ref": f'https://sonar.ch/api/subdivisions/{subdivision["pid"]}'}
            ],
            "masked": "not_masked",
        },
        "status": "in_progress",
        "step": "diffusion",
    }


@pytest.fixture()
def make_deposit(db, deposit_json, bucket_location, pdf_file, make_user, embargo_date):
    """Factory for creating deposit."""

    def _make_deposit(role="submitter", organisation=None):
        user = make_user(role, organisation)

        deposit_json["user"] = {"$ref": f"https://sonar.ch/api/users/{user['pid']}"}

        deposit_json.pop("pid", None)

        record = DepositRecord.create(deposit_json, dbcommit=True, with_bucket=True)

        with open(pdf_file, "rb") as file:
            content = file.read()

        record.files["main.pdf"] = BytesIO(content)
        record.files["main.pdf"]["label"] = "Main file"
        record.files["main.pdf"]["type"] = "file"
        record.files["main.pdf"]["embargoDate"] = embargo_date.isoformat()
        record.files["main.pdf"]["exceptInOrganisation"] = True

        record.files["additional.pdf"] = BytesIO(content)
        record.files["additional.pdf"]["label"] = "Additional file 1"
        record.files["additional.pdf"]["type"] = "file"
        record.files["additional.pdf"]["exceptInOrganisation"] = False

        record.commit()
        record.reindex()
        db.session.commit()

        return record

    return _make_deposit


@pytest.fixture()
def deposit(app, db, user, pdf_file, bucket_location, deposit_json, embargo_date):
    """Deposit fixture."""
    json = copy.deepcopy(deposit_json)
    json["user"] = {"$ref": f"https://sonar.ch/api/users/{user['pid']}"}

    deposit = DepositRecord.create(json, dbcommit=True, with_bucket=True)

    with open(pdf_file, "rb") as file:
        content = file.read()

    deposit.files["main.pdf"] = BytesIO(content)
    deposit.files["main.pdf"]["label"] = "Main file"
    deposit.files["main.pdf"]["type"] = "file"
    deposit.files["main.pdf"]["order"] = 1
    deposit.files["main.pdf"]["embargoDate"] = embargo_date.isoformat()
    deposit.files["main.pdf"]["exceptInOrganisation"] = True

    deposit.files["additional.pdf"] = BytesIO(content)
    deposit.files["additional.pdf"]["label"] = "Additional file 1"
    deposit.files["additional.pdf"]["type"] = "file"
    deposit.files["additional.pdf"]["exceptInOrganisation"] = False

    deposit.commit()
    deposit.reindex()
    db.session.commit()

    return deposit


@pytest.fixture()
def project_json():
    """Project JSON."""
    return {
        "metadata": {
            "name": "Project 1",
            "description": "Description of the project",
            "startDate": "2019-01-01",
            "endDate": "2020-01-01",
            "identifiedBy": {"type": "bf:Local", "source": "RERO", "value": "1111"},
            "investigators": [
                {
                    "agent": {"preferred_name": "John Doe"},
                    "role": ["investigator"],
                    "affiliation": "IST",
                    "identifiedBy": {
                        "type": "bf:Local",
                        "source": "RERO",
                        "value": "2222",
                    },
                }
            ],
            "funding_organisations": [
                {
                    "agent": {"preferred_name": "Funding organisation"},
                    "identifiedBy": {
                        "type": "bf:Local",
                        "source": "RERO",
                        "value": "3333",
                    },
                }
            ],
            "validation": {
                "user": {"$ref": "https://sonar.ch/api/users/orgsubmitter"},
                "status": "validated",
                "action": "save",
            },
        }
    }


@pytest.fixture()
def make_project(app, db, project_json, make_user):
    """Factory for creating project."""

    def _make_project(role="submitter", organisation=None):
        user = make_user(role, organisation)

        project_json["metadata"]["user"] = {
            "$ref": f"https://sonar.ch/api/users/{user['pid']}"
        }

        project_json["metadata"]["organisation"] = {
            "$ref": f"https://sonar.ch/api/organisations/{organisation}"
        }

        project_json.pop("id", None)

        with mock.patch(
            "invenio_records_resources.services.base.service.Service.require_permission"
        ):
            project = sonar.service("projects").create(None, project_json)
        app.extensions["invenio-search"].flush_and_refresh(index="projects")
        return project

    return _make_project


@pytest.fixture()
def project(app, db, es, admin, organisation, project_json):
    """Deposit fixture."""
    json = copy.deepcopy(project_json)
    json["metadata"]["user"] = {"$ref": f"https://sonar.ch/api/users/{admin['pid']}"}
    json["metadata"]["organisation"] = {
        "$ref": f"https://sonar.ch/api/organisations/{organisation['pid']}"
    }

    with mock.patch(
        "invenio_records_resources.services.base.service.Service.require_permission"
    ):
        project = sonar.service("projects").create(None, json)
    app.extensions["invenio-search"].flush_and_refresh(index="projects")
    return project


@pytest.fixture()
def collection_json():
    """Collection JSON."""
    return {
        "name": [{"language": "eng", "value": "Collection name"}],
        "description": [{"language": "eng", "value": "Collection description"}],
    }


@pytest.fixture()
def make_collection(app, db, collection_json):
    """Factory for creating collection."""

    def _make_collection(organisation=None):
        collection_json["organisation"] = {
            "$ref": f"https://sonar.ch/api/organisations/{organisation}"
        }

        collection_json.pop("pid", None)

        collection = CollectionRecord.create(
            collection_json, dbcommit=True, with_bucket=True
        )
        collection.commit()
        collection.reindex()
        db.session.commit()
        return collection

    return _make_collection


@pytest.fixture()
def collection(app, db, es, admin, organisation, collection_json):
    """Collection fixture."""
    json = copy.deepcopy(collection_json)
    json["organisation"] = {
        "$ref": f"https://sonar.ch/api/organisations/{organisation['pid']}"
    }

    collection = CollectionRecord.create(json, dbcommit=True, with_bucket=True)
    collection.commit()
    collection.reindex()
    db.session.commit()
    return collection


@pytest.fixture()
def collection_with_file(collection, pdf_file):
    """Create a collection with a file attached."""
    with open(pdf_file, "rb") as file:
        collection.add_file(file.read(), "test1.pdf")
        collection.commit()
    return collection


@pytest.fixture()
def subdivision_json():
    """Subdivision JSON."""
    return {"name": [{"language": "eng", "value": "Subdivision name"}]}


@pytest.fixture()
def make_subdivision(app, db, subdivision_json):
    """Factory for creating subdivision."""

    def _make_subdivision(organisation=None):
        subdivision_json["organisation"] = {
            "$ref": f"https://sonar.ch/api/organisations/{organisation}"
        }

        subdivision_json.pop("pid", None)

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
    json["organisation"] = {
        "$ref": f"https://sonar.ch/api/organisations/{organisation['pid']}"
    }

    subdivision = SubdivisionRecord.create(json, dbcommit=True)
    subdivision.commit()
    subdivision.reindex()
    db.session.commit()
    return subdivision


@pytest.fixture()
def subdivision2(app, db, es, admin, organisation, subdivision_json):
    """Second subdivision fixture."""
    json = copy.deepcopy(subdivision_json)
    json["organisation"] = {
        "$ref": f"https://sonar.ch/api/organisations/{organisation['pid']}"
    }

    subdivision = SubdivisionRecord.create(json, dbcommit=True)
    subdivision.commit()
    subdivision.reindex()
    db.session.commit()
    return subdivision


@pytest.fixture()
def bucket_location(app, db):
    """Create a default location for managing files."""
    # Create unique name to prefent: `UNIQUE constraint failed: files_location.name`
    # name = uri.split("/")[-1].replace("_", "-").lower()
    uri = tempfile.mkdtemp()
    location_obj = Location(name="default", uri=uri, default=True)
    db.session.add(location_obj)
    db.session.commit()
    yield location_obj
    # Remove folder after test
    if os.path.isdir(uri):
        shutil.rmtree(uri, ignore_errors=True)


@pytest.fixture()
def pdf_file():
    """Return test PDF file path."""
    return os.path.join(os.path.dirname(__file__), "data", "test.pdf")


@pytest.fixture(autouse=True)
def mock_thumbnail_creation(monkeypatch):
    """Mock thumbnail creation for all tests."""
    monkeypatch.setattr(
        "sonar.modules.utils.Image.make_blob",
        lambda *args: b"Fake thumbnail image content",
    )


@pytest.fixture
def without_oaiset_signals(app):
    """Temporary disable oaiset signals."""
    from invenio_oaiserver import current_oaiserver

    current_oaiserver.unregister_signals_oaiset()
    yield
    current_oaiserver.register_signals_oaiset()


@pytest.fixture()
def minimal_thesis_document_with_urn(db, bucket_location, organisation_with_urn):
    """Return a minimal thesis document."""
    with requests_mock.mock() as response:
        response.head(requests_mock.ANY, status_code=404)
        response.post(
            requests_mock.ANY, status_code=201, json={"urn": "urn:nbn:ch:rero-006-17"}
        )
        record = DocumentRecord.create(
            {
                "title": [
                    {
                        "type": "bf:Title",
                        "mainTitle": [
                            {"language": "eng", "value": "Title of the document"}
                        ],
                    }
                ],
                "documentType": "coar:c_db06",
                "organisation": [{"$ref": "https://sonar.ch/api/organisations/org"}],
                "identifiedBy": [
                    {"type": "bf:Local", "value": "10.1186"},
                ],
            },
            dbcommit=True,
            with_bucket=True,
        )
        record.commit()
        db.session.commit()
        record.reindex()
        return record


@pytest.fixture()
def minimal_document(db, bucket_location, organisation):
    """Minimal document."""
    record = DocumentRecord.create(
        {
            "pid": "1000",
            "title": [
                {
                    "type": "bf:Title",
                    "mainTitle": [
                        {"language": "eng", "value": "Title of the document"}
                    ],
                }
            ],
            "organisation": [
                {"$ref": f"https://sonar.ch/api/organisations/{organisation['pid']}"}
            ],
        },
        dbcommit=True,
        with_bucket=True,
    )
    record.commit()
    db.session.commit()
    return record
