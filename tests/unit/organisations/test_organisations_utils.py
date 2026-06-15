# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test organisations utils."""

from sonar.modules.organisations.utils import platform_name


def test_platform_name():
    """Test transformation of platform name."""
    organisation = {"platformName": "#SiteName\n##Platform"}
    assert platform_name(organisation) == "SiteName - Platform"
