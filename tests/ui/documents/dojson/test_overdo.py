# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test base overdo."""

from sonar.modules.documents.dojson.overdo import Overdo


def test_not_repetitve():
    """Test the function not_repetetive."""
    data = Overdo.not_repetitive({"sub": ("first", "second")}, "sub")
    assert data == "first"

    data = Overdo.not_repetitive({"sub": "only"}, "sub", "")
    assert data == "only"
