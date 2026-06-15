# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test SONAR document extension."""

from sonar.modules.documents.ext import Documents


def test_init(app):
    """Test extension constructor."""
    documents = Documents(app)
    assert isinstance(documents, Documents)
