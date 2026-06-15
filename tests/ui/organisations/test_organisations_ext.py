# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test SONAR organisation extension."""

from sonar.modules.organisations.ext import Organisations


def test_init(app):
    """Test extension constructor."""
    organisations = Organisations(app)
    assert isinstance(organisations, Organisations)
