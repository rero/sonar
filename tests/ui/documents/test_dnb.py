# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test DnbUrnService API."""

import requests_mock

from sonar.modules.documents.dnb import DnbUrnService


def test_dnb_sucessor(app):
    """Test a successor assignment."""
    with requests_mock.mock() as response:
        response.patch(requests_mock.ANY, status_code=204)
        DnbUrnService().set_successor("urn:nbn:ch:rero-002-old", "urn:nbn:ch:rero-002-new")
