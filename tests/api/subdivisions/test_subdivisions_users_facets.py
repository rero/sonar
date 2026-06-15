# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test subdivisions facets in users."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, db, client, deposit, superuser, subdivision):
    """Test subdivision facet."""
    superuser["subdivision"] = {"$ref": f"https://sonar.ch/api/subdivisions/{subdivision['pid']}"}
    superuser.commit()
    db.session.commit()
    superuser.reindex()

    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("invenio_records_rest.user_list"))
    assert res.status_code == 200
    assert res.json["aggregations"]["subdivision"]["buckets"] == [
        {"key": "2", "doc_count": 1, "name": "Subdivision name"}
    ]
