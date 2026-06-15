# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test extension before request."""

from flask import request, url_for
from invenio_accounts.testutils import login_user_via_session


def test_ext_before_request(client, superuser):
    """Test before request hook in extension."""
    login_user_via_session(client, email=superuser["email"])

    res = client.get(url_for("projects.search"))
    assert res.status_code == 200
    assert request.accept_mimetypes.find("text/csv") == -1

    res = client.get(url_for("projects.search", format="text/csv"))
    assert res.status_code == 200
    assert request.accept_mimetypes.find("text/csv") == 0
