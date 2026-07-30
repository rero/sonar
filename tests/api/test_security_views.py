# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Flask-Security views on the API application."""


def test_security_ui_views_not_registered(app):
    """Test that the Flask-Security views are not registered on the API.

    They render SONAR templates, which are only available on the UI
    application, so requesting them through `/api` raised a `TemplateNotFound`
    error.
    """
    assert not [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith("security.")]


def test_security_ui_view_not_found(client):
    """Test that a Flask-Security URL is not served by the API."""
    res = client.get("/login/")
    assert res.status_code == 404
