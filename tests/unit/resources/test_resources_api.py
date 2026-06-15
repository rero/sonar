# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test resources API."""


def test_index_name_property(project):
    """Test getting index name"""
    assert project._record.index_name == "projects"
