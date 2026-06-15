# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Dublic Core marshmallow schema."""

import re
from copy import deepcopy
from unittest import mock

import requests_mock
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from sonar.modules.documents.api import DocumentIndexer, DocumentRecord
from sonar.modules.documents.urn import Urn


def test_urn_get_generate_urns(organisation_with_urn, document):
    """Test get documents that need a URN code."""
    document.pop("identifiedBy")
    document["documentType"] = "coar:c_db06"
    document.reindex()
    assert next(iter(Urn.get_documents_to_generate_urns()))["pid"] == document["pid"]
    # restore original data
    indexer = DocumentIndexer()
    doc = DocumentRecord.get_record_by_pid(document["pid"])
    indexer.index(doc)


def test_urn_create(app, db, bucket_location, organisation_with_urn):
    """Test create URN identifier for a shared organisation."""
    organisation = organisation_with_urn
    doc_data = {
        "title": [
            {
                "type": "bf:Title",
                "mainTitle": [{"language": "eng", "value": "Title of the document"}],
            }
        ],
        "documentType": "coar:c_db06",
        "organisation": [{"$ref": "https://sonar.ch/api/organisations/org"}],
        "identifiedBy": [
            {"type": "bf:Local", "value": "10.1186"},
        ],
    }

    from sonar.modules.documents.urn import UrnIdentifier

    # mock the next URN id
    with mock.patch.object(UrnIdentifier, "next") as mock_method:
        urn = "urn:nbn:ch:rero-006-17"
        mock_method.return_value = "1"
        with requests_mock.Mocker() as req_mock:
            url_matcher = re.compile(rf"{app.config.get('SONAR_APP_URN_DNB_BASE_URL')}")
            req_mock.head(url_matcher, status_code=404)
            # simulate the return value of the DBN server
            req_mock.post(url_matcher, status_code=201, json={"urn": urn})

            record = DocumentRecord.create(deepcopy(doc_data), dbcommit=True, with_bucket=True)

            # two dnb requests, head and post
            assert req_mock.call_count == 2
            # the second request is the post, the first is the head
            request = req_mock.request_history[1]
            base_url = "https://" + app.config.get("SONAR_APP_SERVER_NAME")
            assert request.json()["urls"][0]["url"] == f"{base_url}/{organisation['code']}/documents/{record['pid']}"
            record.commit()
            db.session.commit()
            record.reindex()
            urn_code = DocumentRecord.get_rero_urn_code(record)
            assert urn_code == urn
            urn_pid = PersistentIdentifier.get("urn", urn_code)
            assert urn_pid.status == PIDStatus.REGISTERED
            # urns = Urn.get_unregistered_urns()
            # assert urn not in urns
            # # should never happens
            # record.delete(dbcommit=True, delindex=True)
            # urn_pid = PersistentIdentifier.get('urn', urn_code)
            # assert urn_pid.status == PIDStatus.DELETED

    with mock.patch.object(UrnIdentifier, "next") as mock_method:
        urn = "urn:nbn:ch:rero-006-24"
        mock_method.return_value = "2"
        organisation.update(
            {
                "code": "foo",
                "isDedicated": True,
                "serverName": "foo.org",
                "platformName": "Foo University",
            }
        )
        organisation.commit()
        with requests_mock.Mocker() as req_mock:
            url_matcher = re.compile(rf"{app.config.get('SONAR_APP_URN_DNB_BASE_URL')}")
            req_mock.head(url_matcher, status_code=404)
            # simulate the return value of the DBN server
            req_mock.post(url_matcher, status_code=201, json={"urn": urn})

            record = DocumentRecord.create(deepcopy(doc_data), dbcommit=True, with_bucket=True)

            # two dnb requests, head and post
            assert req_mock.call_count == 2
            # the second request is the post, the first is the head
            request = req_mock.request_history[1]
            base_url = f"https://{organisation['serverName']}"
            assert request.json()["urls"][0]["url"] == f"{base_url}/{organisation['code']}/documents/{record['pid']}"
            record.commit()
            db.session.commit()
            record.reindex()
            urn_code = DocumentRecord.get_rero_urn_code(record)
            assert urn_code == urn
            urn_pid = PersistentIdentifier.get("urn", urn_code)
            assert urn_pid.status == PIDStatus.REGISTERED
            urns = Urn.get_unregistered_urns()
            assert urn not in urns
            # should never happens
            record.delete(dbcommit=True, delindex=True)
            urn_pid = PersistentIdentifier.get("urn", urn_code)
            assert urn_pid.status == PIDStatus.DELETED
            # db.session.rollback() ????

    with mock.patch.object(UrnIdentifier, "next") as mock_method:
        urn = "urn:nbn:ch:rero-006-37"
        mock_method.return_value = "3"
        organisation.update({"isDedicated": False, "isShared": False, "code": "foo"})
        organisation.commit()
        with requests_mock.Mocker() as req_mock:
            url_matcher = re.compile(rf"{app.config.get('SONAR_APP_URN_DNB_BASE_URL')}")
            req_mock.head(url_matcher, status_code=404)
            # simulate the return value of the DBN server
            req_mock.post(url_matcher, status_code=201, json={"urn": urn})

            record = DocumentRecord.create(deepcopy(doc_data), dbcommit=True, with_bucket=True)

            # two dnb requests, head and post
            assert req_mock.call_count == 2
            # the second request is the post, the first is the head
            request = req_mock.request_history[1]
            base_url = "https://" + app.config.get("SONAR_APP_SERVER_NAME")
            assert request.json()["urls"][0]["url"] == f"{base_url}/global/documents/{record['pid']}"
            record.commit()
            db.session.commit()
            record.reindex()
            urn_code = DocumentRecord.get_rero_urn_code(record)
            assert urn_code == urn
            urn_pid = PersistentIdentifier.get("urn", urn_code)
            assert urn_pid.status == PIDStatus.REGISTERED
            urns = Urn.get_unregistered_urns()
            assert urn not in urns
            # should never happens
            record.delete(dbcommit=True, delindex=True)
            urn_pid = PersistentIdentifier.get("urn", urn_code)
            assert urn_pid.status == PIDStatus.DELETED
            db.session.rollback()
