# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test SONAR extension."""

from sonar.modules.shibboleth_authenticator.ext import ShibbolethAuthenticator


def test_init(app):
    """Test extension constructor."""
    auth = ShibbolethAuthenticator(app)
    assert isinstance(auth, ShibbolethAuthenticator)
