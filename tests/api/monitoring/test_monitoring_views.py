# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test monitoring views."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def test_search_db_counts(client, search_clear, superuser, document):
    """The shared monitoring counts every SONAR record type, the projects included."""
    login_user_via_session(client, email=superuser["email"])

    response = client.get(url_for("api_monitoring.search_db_counts", delay=0))
    assert response.status_code == 200
    assert response.json == {
        "data": {
            "depo": {"db": 0, "search": 0, "db-search": 0, "index": "deposits"},
            "doc": {"db": 1, "search": 1, "db-search": 0, "index": "documents"},
            "org": {"db": 1, "search": 1, "db-search": 0, "index": "organisations"},
            "projects": {"db": 0, "search": 0, "db-search": 0, "index": "projects"},
            "user": {"db": 1, "search": 1, "db-search": 0, "index": "users"},
            "coll": {"db": 0, "search": 0, "db-search": 0, "index": "collections"},
            "subd": {"db": 0, "search": 0, "db-search": 0, "index": "subdivisions"},
            "stat": {"db": 0, "search": 0, "db-search": 0, "index": "stats"},
        }
    }


def test_urn(client, search_clear, admin, superuser, minimal_thesis_document_with_urn):
    """Test unregistered urn counts."""
    response = client.get(url_for("sonar_monitoring.urn"))
    assert response.status_code == 401

    login_user_via_session(client, email=admin["email"])
    response = client.get(url_for("sonar_monitoring.urn"))
    assert response.status_code == 403

    login_user_via_session(client, email=superuser["email"])
    response = client.get(url_for("sonar_monitoring.urn"))
    assert response.status_code == 200
    assert response.json["data"]["reserved"]["count"] == 0

    response = client.get(url_for("sonar_monitoring.urn", days=100))
    assert response.status_code == 200
    assert response.json["data"]["reserved"]["count"] == 0

    query = PersistentIdentifier.query.filter_by(pid_type="urn").filter_by(status=PIDStatus.REGISTERED)
    pid = query.first()
    pid.status = PIDStatus.RESERVED
    db.session.commit()
    response = client.get(url_for("sonar_monitoring.urn"))
    assert response.status_code == 200
    assert response.json["data"]["reserved"]["count"] == 1
