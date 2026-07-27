# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test subdivisions facets in documents."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, db, client, document, subdivision, superuser):
    """Test subdivision facet on documents list."""
    document["subdivisions"] = [{"$ref": f"https://sonar.ch/api/subdivisions/{subdivision['pid']}"}]
    document.commit()
    db.session.commit()
    document.reindex()

    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("invenio_records_rest.doc_list", view="org"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1
    assert res.json["aggregations"]["subdivision"]["buckets"] == [
        {"key": "2", "doc_count": 1, "name": "Subdivision name"}
    ]
