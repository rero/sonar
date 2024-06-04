# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test translations REST endpoints."""

from flask import url_for
from mock import patch


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
    assert res.json["About SONAR"] == "À propos de SONAR"
