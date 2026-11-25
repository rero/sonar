# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test organisations REST API."""

import json

import pytest
from flask import url_for
from invenio_accounts.testutils import login_user_via_session

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
THEME = {"primaryColor": "#ABCDEF", "css": ".bg-header { color: red; }"}


def set_theme(db, organisation, theme):
    """Store a theme on an organisation."""
    organisation["theme"] = theme
    organisation.commit()
    db.session.commit()


@pytest.mark.parametrize(
    "changes",
    [
        {"pid": "org"},
        {"pid": "org", "theme": {"primaryColor": "#123456"}},
        {},
        {"pid": "other"},
    ],
)
def test_update_keeps_theme(client, db, organisation, make_organisation, admin, changes):
    """Keep the theme managed by the CLI whatever the body of an update contains."""
    set_theme(db, organisation, THEME)
    set_theme(db, make_organisation("other"), {"primaryColor": "#123456"})

    data = organisation.dumps()
    data.pop("pid")
    data.pop("theme")
    data.update(changes)

    login_user_via_session(client, email=admin["email"])
    res = client.put(
        url_for("invenio_records_rest.org_item", pid_value=organisation["pid"]),
        data=json.dumps(data),
        headers=HEADERS,
    )

    assert res.status_code == 200
    assert res.json["metadata"]["theme"] == THEME


def test_create_ignores_theme(client, superuser):
    """Do not store a theme sent when creating an organisation."""
    data = {"code": "org2", "name": "org2", "theme": THEME}

    login_user_via_session(client, email=superuser["email"])
    res = client.post(url_for("invenio_records_rest.org_list"), data=json.dumps(data), headers=HEADERS)

    assert res.status_code == 201
    assert "theme" not in res.json["metadata"]
