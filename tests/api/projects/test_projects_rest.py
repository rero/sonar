# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test projects rest API."""

import json

import pytest
from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from werkzeug.http import unquote_etag

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def revision(response):
    """Return the bare revision number held by the ETag of a response."""
    return unquote_etag(response.headers["ETag"])[0]


@pytest.mark.parametrize("if_match", ['"{revision}"', 'W/"{revision}"', "{revision}"], ids=["quoted", "weak", "bare"])
def test_update_delete_with_etag(client, make_project, admin, project_json, if_match):
    """Test that every representation of the ETag is accepted in `If-Match`."""
    # `project.id` and `project_json` are used instead of dumping the record, as a
    # dump resolves `current_user` outside of a request and voids the login below.
    project = make_project("submitter", "org")
    login_user_via_session(client, email=admin["email"])
    url = url_for("projects.read", pid_value=project.id)
    data = json.dumps(project_json)

    res = client.get(url)
    assert res.status_code == 200
    assert res.headers["ETag"].startswith('"')
    stale = if_match.format(revision=revision(res))

    # The revision is accepted whichever representation carries it.
    res = client.put(url, data=data, headers=HEADERS | {"If-Match": stale})
    assert res.status_code == 200
    current = if_match.format(revision=revision(res))
    assert current != stale

    # An outdated revision is still rejected.
    res = client.put(url, data=data, headers=HEADERS | {"If-Match": stale})
    assert res.status_code == 412

    res = client.delete(url, headers=HEADERS | {"If-Match": current})
    assert res.status_code == 204


def test_update_delete_with_etag_wildcard(client, make_project, admin, project_json):
    """Test that a wildcard `If-Match` matches any revision of the record."""
    project = make_project("submitter", "org")
    login_user_via_session(client, email=admin["email"])
    url = url_for("projects.read", pid_value=project.id)
    data = json.dumps(project_json)

    res = client.put(url, data=data, headers=HEADERS | {"If-Match": "*"})
    assert res.status_code == 200

    res = client.delete(url, headers=HEADERS | {"If-Match": "*"})
    assert res.status_code == 204


def test_update_with_several_etags(client, make_project, admin, project_json):
    """Test that an `If-Match` listing several tags is rejected."""
    project = make_project("submitter", "org")
    login_user_via_session(client, email=admin["email"])
    url = url_for("projects.read", pid_value=project.id)

    res = client.get(url)
    res = client.put(
        url,
        data=json.dumps(project_json),
        headers=HEADERS | {"If-Match": f'{res.headers["ETag"]}, "42"'},
    )
    assert res.status_code == 400
