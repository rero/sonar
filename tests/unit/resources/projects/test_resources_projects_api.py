# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test resources projects API."""


def test_to_string(project):
    """Test string representation of object."""
    assert str(project._record) == "Project 1"
