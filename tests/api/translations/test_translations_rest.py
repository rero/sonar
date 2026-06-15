# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test translations REST endpoints."""

from unittest.mock import patch

from flask import url_for


def test_get_translations(client):
    """Test get translations."""
    # Non existing language
    res = client.get(url_for("translations.get_translations", lang="un"))
    assert res.status_code == 404

    # Error during translation parsing
    with patch("polib.pofile", side_effect=Exception("Mocked error")):
        res = client.get(url_for("translations.get_translations", lang="fr"))
        assert res.status_code == 404

    # OK
    res = client.get(url_for("translations.get_translations", lang="fr"))
    assert res.status_code == 200
    assert res.json["Help"] == "Aide"
