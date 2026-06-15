# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test HEG webdav client."""

from sonar.webdav import HegClient


def test_init(app):
    """Test init."""
    client = HegClient()
    assert client.webdav.hostname == "https://share.rero.ch/HEG"
