# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test monitoring views."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def test_data_info(client, search_clear, superuser, document, monkeypatch):
    """Test integrity info."""
    login_user_via_session(client, email=superuser["email"])

    response = client.get(url_for("monitoring_api.data_info"))
    assert response.status_code == 200
    assert response.json == {
        "data": {
            "depo": {"db": 0, "es": 0, "db-es": 0, "index": "deposits"},
            "doc": {"db": 1, "es": 1, "db-es": 0, "index": "documents"},
            "org": {"db": 1, "es": 1, "db-es": 0, "index": "organisations"},
            "projects": {"db": 0, "es": 0, "db-es": 0, "index": "projects"},
            "user": {"db": 1, "es": 1, "db-es": 0, "index": "users"},
            "coll": {"db": 0, "es": 0, "db-es": 0, "index": "collections"},
            "subd": {"db": 0, "es": 0, "db-es": 0, "index": "subdivisions"},
            "stat": {"db": 0, "es": 0, "db-es": 0, "index": "stats"},
        }
    }

    # With detail
    response = client.get(url_for("monitoring_api.data_info", detail=True))
    assert response.status_code == 200
    assert response.json["data"]["doc"]["detail"] == {
        "db": [],
        "es": [],
        "es_double": [],
    }

    # Throw error
    def mock_info(*args, **kwargs):
        raise Exception("Unknown exception")

    monkeypatch.setattr("sonar.monitoring.api.data_integrity.DataIntegrityMonitoring.info", mock_info)
    response = client.get(url_for("monitoring_api.data_info", detail=True))
    assert response.status_code == 500


def test_db_connection_count(client, search_clear, monkeypatch, admin, superuser):
    """Test DB connections count."""
    # Not logged
    response = client.get(url_for("monitoring_api.db_connection_count"))
    assert response.status_code == 401

    login_user_via_session(client, email=admin["email"])

    # Wrong role
    response = client.get(url_for("monitoring_api.db_connection_count"))
    assert response.status_code == 403

    login_user_via_session(client, email=superuser["email"])

    # need to be mocked as it works only with postgresql
    class MockConnectionQuery:
        """Mock connection query."""

        def first(self):
            """Simulate returning the first result."""
            return (100, 10, 2, 88)

    monkeypatch.setattr(db.session, "execute", lambda *args: MockConnectionQuery())

    # OK
    response = client.get(url_for("monitoring_api.db_connection_count"))
    assert response.status_code == 200
    assert response.json == {"data": {"max": 100, "used": 10, "reserved_for_super": 2, "free": 88}}


def test_db_activity(client, search_clear, monkeypatch, admin, superuser):
    """Test DB activity."""
    login_user_via_session(client, email=superuser["email"])

    # need to be mocked as it works only with postgresql
    class MockActivityQuery:
        """Mock activity query."""

        def fetchall(self):
            """Simulate returning the results."""
            return [
                (
                    "PID",
                    "",
                    "10.233.92.25",
                    33382,
                    "Mon, 08 Feb 2021 10:46:55 GMT",
                    "Mon, 08 Feb 2021 10:46:56 GMT",
                    "Mon, 08 Feb 2021 10:46:57 GMT",
                    None,
                    "active",
                    "\n        SELECT\n            pid, application_name, client",
                )
            ]

    monkeypatch.setattr(db.session, "execute", lambda *args: MockActivityQuery())

    # Error
    response = client.get(url_for("monitoring_api.db_activity"))
    assert response.status_code == 200
    assert response.json == {
        "data": {
            "PID": {
                "application_name": "",
                "client_addr": "10.233.92.25",
                "client_port": 33382,
                "backend_start": "Mon, 08 Feb 2021 10:46:55 GMT",
                "xact_start": "Mon, 08 Feb 2021 10:46:56 GMT",
                "query_start": "Mon, 08 Feb 2021 10:46:57 GMT",
                "wait_event": None,
                "state": "active",
                "left": "\n        SELECT\n            pid, application_name, client",
            }
        }
    }


def test_data_status(client, search_clear, organisation, superuser, document, monkeypatch):
    """Test integrity status."""
    login_user_via_session(client, email=superuser["email"])

    # OK
    response = client.get(url_for("monitoring_api.data_status"))
    assert response.status_code == 200
    assert response.json == {"data": {"status": "green"}}

    # Has error
    document.delete()
    response = client.get(url_for("monitoring_api.data_status"))
    assert response.status_code == 200
    assert response.json == {"data": {"status": "red"}}

    # Throw error
    def mock_info(*args):
        raise Exception("Unknown exception")

    monkeypatch.setattr("sonar.monitoring.api.data_integrity.DataIntegrityMonitoring.info", mock_info)
    response = client.get(url_for("monitoring_api.data_status"))
    assert response.status_code == 500


def test_elastic_search(client, superuser, monkeypatch):
    """Test elastic search health."""
    login_user_via_session(client, email=superuser["email"])

    response = client.get(url_for("monitoring_api.elastic_search"))
    assert response.status_code == 200
    assert "active_primary_shards" in response.json["data"]
    assert "status" in response.json["data"]

    # Throw error
    def mock_info(*args):
        raise Exception("Unknown exception")

    monkeypatch.setattr("invenio_search.current_search_client.cluster.health", mock_info)
    response = client.get(url_for("monitoring_api.elastic_search"))
    assert response.status_code == 500
    assert response.json == {"error": "Unknown exception"}


def test_urn(client, search_clear, superuser, monkeypatch, minimal_thesis_document_with_urn):
    """Test unregistered urn counts."""
    login_user_via_session(client, email=superuser["email"])
    response = client.get(url_for("monitoring_api.urn"))
    assert response.status_code == 200
    assert response.json["data"]["reserved"]["count"] == 0

    response = client.get(url_for("monitoring_api.urn", days=100))
    assert response.status_code == 200
    assert response.json["data"]["reserved"]["count"] == 0

    query = PersistentIdentifier.query.filter_by(pid_type="urn").filter_by(status=PIDStatus.REGISTERED)
    pid = query.first()
    pid.status = PIDStatus.RESERVED
    db.session.commit()
    response = client.get(url_for("monitoring_api.urn"))
    assert response.status_code == 200
    assert response.json["data"]["reserved"]["count"] == 1
