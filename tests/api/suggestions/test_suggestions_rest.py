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

"""Test suggestions rest."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from invenio_search import current_search


def test_completion(client, project_json, make_user):
    """Test completion suggestions."""
    user = make_user("admin", organisation="hepvs", access="admin-access")
    login_user_via_session(client, email=user["email"])

    project_json["metadata"]["projectSponsor"] = "Sponsor 1"
    res = client.post(url_for("projects.search"), data=json.dumps(project_json))
    # Ensure project is indexed
    current_search.flush_and_refresh(index="projects")

    # No query parameter
    res = client.get(url_for("suggestions.completion"))
    assert res.status_code == 400
    assert res.json == {"error": "No query parameter given"}

    # No field parameter
    res = client.get(url_for("suggestions.completion", q="test"))
    assert res.status_code == 400
    assert res.json == {"error": "No field parameter given"}

    # No resource parameter
    res = client.get(
        url_for(
            "suggestions.completion", q="Sp", field="metadata.projectSponsor.suggest"
        )
    )
    assert res.status_code == 400
    assert res.json == {"error": "No resource parameter given"}

    # Non existing resource
    res = client.get(
        url_for(
            "suggestions.completion",
            q="Sp",
            field="metadata.projectSponsor.suggest",
            resource="unknown",
        )
    )
    assert res.status_code == 404
    assert res.json == {"error": "Search class not found"}

    # Unknown field
    res = client.get(
        url_for("suggestions.completion", q="Sp", field="unknown", resource="projects")
    )
    assert res.status_code == 400
    assert res.json == {"error": "Bad request"}

    # OK
    res = client.get(
        url_for(
            "suggestions.completion",
            q="Spo",
            field="metadata.projectSponsor.suggest",
            resource="projects",
        )
    )
    assert res.status_code == 200
    assert res.json == ["Sponsor 1"]

    # Old way resource
    res = client.get(
        url_for(
            "suggestions.completion",
            q="Hepvs",
            field="full_name.suggest",
            resource="users",
        )
    )
    assert res.status_code == 200
    assert res.json == ["Hepvsadmin Doe"]
