# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test subdivisions facets in deposits."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, db, client, deposit, superuser):
    """Test subdivision facet."""
    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("invenio_records_rest.depo_list"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1
    assert res.json["aggregations"]["subdivision"]["buckets"] == [
        {"key": "2", "doc_count": 1, "name": "Subdivision name"}
    ]
