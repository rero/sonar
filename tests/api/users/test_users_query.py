# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test users queries."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_queries(client, superuser, make_user):
    """Test the query user list filtering."""
    login_user_via_session(client, email=superuser["email"])

    headers = [("Content-Type", "application/json")]

    # No user found
    response = client.get(
        url_for("invenio_records_rest.user_list", missing_organisation="1"),
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["hits"]["total"]["value"] == 0

    # 1 user found
    make_user("user", None)
    response = client.get(
        url_for("invenio_records_rest.user_list", missing_organisation="1"),
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["hits"]["total"]["value"] == 1
