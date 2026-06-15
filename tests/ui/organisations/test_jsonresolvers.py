# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test organisations jsonresolvers."""


def test_organisation_resolver(document):
    """Test organisation resolver."""
    assert document["organisation"][0].get("$ref")
    assert document["organisation"][0]["$ref"] == "https://sonar.ch/api/organisations/org"

    assert document.resolve().get("organisation")[0]["name"] == "org"
