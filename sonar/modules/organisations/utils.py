# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Utils functions for organisations module."""

import markdown
from bs4 import BeautifulSoup


def platform_name(organisation):
    """Get platform name."""
    platform_name = organisation.get("platformName")
    if platform_name:
        html = markdown.markdown(platform_name)
        return "".join(BeautifulSoup(html).findAll(text=True)).replace("\n", " - ")
    return None
