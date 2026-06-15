# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test SONAR fetchers."""

from sonar.modules.documents.api import DocumentRecord


def test_id_fetcher():
    """Test id fetcher."""
    assert DocumentRecord.fetcher("1", {"pid": "1"}).pid_value == "1"
