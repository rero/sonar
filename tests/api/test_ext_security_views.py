# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Flask-Security views on the API application."""

import pytest
from flask import url_for
from flask_security import url_for_security


@pytest.mark.parametrize(
    "endpoint, kwargs",
    [
        ("security.change_password", {}),
        ("security.forgot_password", {}),
        ("security.login", {}),
        ("security.register", {}),
        ("security.reset_password", {"token": "token"}),
        ("security.send_confirmation", {}),
    ],
)
def test_security_ui_views_disabled(client, endpoint, kwargs):
    """Test that views rendering a template are not served by the API."""
    res = client.get(url_for(endpoint, **kwargs))
    assert res.status_code == 404


def test_security_ui_views_url_still_available(app):
    """Test that links to the UI application can still be generated."""
    assert url_for_security("reset_password", token="token")


def test_security_logout_view_available(client):
    """Test that logout is still served, as it does not render a template."""
    res = client.get(url_for_security("logout"))
    assert res.status_code == 302
