# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test authenticator handler."""

import pytest

from sonar.modules.shibboleth_authenticator.handlers import authorized_signup_handler


def test_authorized_signup_handler(app, roles, valid_sp_configuration, valid_attributes, monkeypatch):
    """Test signup handler."""
    app.config.update(SHIBBOLETH_SERVICE_PROVIDER=valid_sp_configuration)

    class MockResponse:
        """Mock SAML auth object."""

        def get_attributes(self):
            """Return valid attributes for authentication."""
            return valid_attributes

    auth = MockResponse()

    # Unavailable configuration
    with pytest.raises(KeyError):
        authorized_signup_handler(auth, None)

    # Test valid configuration
    assert authorized_signup_handler(auth, "idp").status_code == 302

    # Test redirect to next url
    monkeypatch.setattr(
        "sonar.modules.shibboleth_authenticator.handlers.get_session_next_url",
        lambda remote_app: "/test/",
    )
    response = authorized_signup_handler(auth, "idp")
    assert response.status_code == 302
    assert "/test/" in response.location

    class MockUser:
        """Mock user."""

        def is_authenticated(self):
            """Return if user is authenticated."""
            return False

    # Test oauth authentication failure
    monkeypatch.setattr(
        "sonar.modules.shibboleth_authenticator.handlers.oauth_authenticate",
        lambda remote, user, require_existing_link: False,
    )
    response = authorized_signup_handler(auth, "idp")
    assert response.status_code == 302
    assert "/login/" in response.location

    # Test oauth register failure
    monkeypatch.setattr("sonar.modules.shibboleth_authenticator.handlers.current_user", MockUser())
    monkeypatch.setattr(
        "sonar.modules.shibboleth_authenticator.handlers.oauth_get_user",
        lambda remote, account_info: None,
    )
    monkeypatch.setattr(
        "sonar.modules.shibboleth_authenticator.handlers.get_account_info",
        lambda *args: {"user": {}},
    )
    monkeypatch.setattr(
        "sonar.modules.shibboleth_authenticator.handlers.oauth_register",
        lambda form: None,
    )
    response = authorized_signup_handler(auth, "idp")
    assert response.status_code == 302
    assert "/login/" in response.location
