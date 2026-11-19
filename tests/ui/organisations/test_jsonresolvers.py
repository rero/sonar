# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test organisations jsonresolvers."""


def test_organisation_resolver(document):
    """Test organisation resolver."""
    assert document["organisation"][0].get("$ref")
    assert document["organisation"][0]["$ref"] == "https://sonar.ch/api/organisations/org"

    assert document.resolve().get("organisation")[0]["name"] == "org"


def test_organisation_resolver_leaves_theme_out(db, document, organisation):
    """Leave the theme out, so that its CSS is not indexed with each document."""
    organisation["theme"] = {"primaryColor": "#ABCDEF", "css": ".bg-header { background-color: red; }"}
    organisation.commit()
    db.session.commit()

    assert "theme" not in document.resolve()["organisation"][0]
