# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test projects filters."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_filters(client, superuser, project, make_project):
    """Test projects filters."""
    make_project("submitter", "org")

    login_user_via_session(client, email=superuser["email"])

    # Without filter
    res = client.get(url_for("projects.search"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
    assert len(res.json["aggregations"]["user"]["buckets"]) == 2

    # Existing user filter
    res = client.get(url_for("projects.search", user="orgadmin"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert len(res.json["aggregations"]["user"]["buckets"]) == 1

    # Non existing organisation filter
    res = client.get(url_for("projects.search", user="unknown"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0
    assert not res.json["aggregations"]["user"]["buckets"]
