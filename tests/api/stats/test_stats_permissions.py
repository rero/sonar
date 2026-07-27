# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test stats permissions."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session

from sonar.modules.stats.api import Record


def test_list(app, client, document, superuser, admin, moderator, submitter, user, search_clear):
    """Test list stats permissions."""
    # Not logged
    res = client.get(url_for("invenio_records_rest.stat_list"))
    assert res.status_code == 401

    for logged_user in [superuser, admin, moderator, submitter, user]:
        login_user_via_session(client, email=logged_user["email"])
        res = client.get(url_for("invenio_records_rest.stat_list"))
        assert res.status_code == 403


def test_create(client, superuser, admin, moderator, submitter, user, search_clear):
    """Test create stats permissions."""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Not logged
    res = client.post(url_for("invenio_records_rest.stat_list"), data=json.dumps({}), headers=headers)
    assert res.status_code == 401

    for logged_user in [superuser, admin, moderator, submitter, user]:
        login_user_via_session(client, email=logged_user["email"])
        res = client.post(
            url_for("invenio_records_rest.stat_list"),
            data=json.dumps({}),
            headers=headers,
        )
        assert res.status_code == 403


def test_read(client, document, superuser, admin, moderator, submitter, user, search_clear):
    """Test read stats permissions."""
    record = Record.collect()

    # Not logged
    res = client.get(url_for("invenio_records_rest.stat_item", pid_value=record["pid"]))
    assert res.status_code == 401

    for logged_user in [admin, moderator, submitter, user]:
        login_user_via_session(client, email=logged_user["email"])
        res = client.get(url_for("invenio_records_rest.stat_item", pid_value=record["pid"]))
        assert res.status_code == 403

    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("invenio_records_rest.stat_item", pid_value=record["pid"]))
    assert res.status_code == 200

    # CSV
    res = client.get(url_for("invenio_records_rest.stat_item", format="text/csv", pid_value=record["pid"]))
    assert res.status_code == 200
    assert res.data == b"organisation,type,documents,full_text,no_full_text\r\norg,shared,1,0,1\r\n"


def test_update(client, superuser, admin, moderator, submitter, user, search_clear):
    """Test update stats permissions."""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    record = Record.collect()

    # Not logged
    res = client.put(
        url_for("invenio_records_rest.stat_item", pid_value=record["pid"]),
        data=json.dumps(record.dumps()),
        headers=headers,
    )
    assert res.status_code == 401

    for logged_user in [superuser, admin, moderator, submitter, user]:
        login_user_via_session(client, email=logged_user["email"])
        res = client.put(
            url_for("invenio_records_rest.stat_item", pid_value=record["pid"]),
            data=json.dumps(record.dumps()),
            headers=headers,
        )
        assert res.status_code == 403


def test_delete(client, superuser, admin, moderator, submitter, user, search_clear):
    """Test delete stats permissions."""
    record = Record.collect()

    res = client.delete(url_for("invenio_records_rest.stat_item", pid_value=record["pid"]))
    assert res.status_code == 401

    for logged_user in [superuser, admin, moderator, submitter, user]:
        login_user_via_session(client, email=logged_user["email"])
        res = client.delete(url_for("invenio_records_rest.stat_item", pid_value=record["pid"]))
        assert res.status_code == 403
