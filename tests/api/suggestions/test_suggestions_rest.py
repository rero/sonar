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


def test_completion(client, project_hepvs_json, make_user, user_without_role):
    """Test completion suggestions with access control and organisation filter."""
    # 401: unauthenticated request blocked before parameter validation
    res = client.get(url_for("suggestions.completion"))
    assert res.status_code == 401

    # 403: authenticated but no submitter role
    login_user_via_session(client, email=user_without_role.email)
    res = client.get(url_for("suggestions.completion", q="test", field="metadata.name", resource="projects"))
    assert res.status_code == 403

    headers = {"Content-Type": "application/json"}

    # Setup: hepvs admin (dedicated org with hepvs schema) + project
    user_hepvs = make_user("admin", organisation="hepvs", organisation_is_shared=False, access="admin-access")
    login_user_via_session(client, email=user_hepvs["email"])

    hepvs_project = project_hepvs_json
    hepvs_project["metadata"]["name"] = "HEPVS Research Project"
    hepvs_project["metadata"]["organisation"] = {"$ref": "https://sonar.ch/api/organisations/hepvs"}
    hepvs_project["metadata"]["user"] = {"$ref": f"https://sonar.ch/api/users/{user_hepvs['pid']}"}
    res = client.post(url_for("projects.search"), data=json.dumps(hepvs_project), headers=headers)
    assert res.status_code == 201

    # Setup: usi admin (shared org, default schema) + project
    user_usi = make_user("admin", organisation="usi", access="admin-access")
    login_user_via_session(client, email=user_usi["email"])

    usi_project = {
        "metadata": {
            "name": "USI Research Project",
            "startDate": "2021-01-01",
            "organisation": {"$ref": "https://sonar.ch/api/organisations/usi"},
            "user": {"$ref": f"https://sonar.ch/api/users/{user_usi['pid']}"},
        }
    }
    res = client.post(url_for("projects.search"), data=json.dumps(usi_project), headers=headers)
    assert res.status_code == 201

    current_search.flush_and_refresh(index="projects")

    # Switch back to hepvs admin for parameter validation tests
    login_user_via_session(client, email=user_hepvs["email"])

    # No query parameter
    res = client.get(url_for("suggestions.completion"))
    assert res.status_code == 400
    assert res.json == {"error": "No query parameter given"}

    # No field parameter
    res = client.get(url_for("suggestions.completion", q="test"))
    assert res.status_code == 400
    assert res.json == {"error": "No field parameter given"}

    # No resource parameter
    res = client.get(url_for("suggestions.completion", q="Research", field="metadata.name"))
    assert res.status_code == 400
    assert res.json == {"error": "No resource parameter given"}

    # Non-existent resource
    res = client.get(
        url_for(
            "suggestions.completion",
            q="Research",
            field="metadata.name",
            resource="unknown",
        )
    )
    assert res.status_code == 404
    assert res.json == {"error": "Search class not found"}

    # Unknown field returns empty results (match_phrase_prefix silently ignores unmapped fields)
    res = client.get(url_for("suggestions.completion", q="Research", field="unknown", resource="projects"))
    assert res.status_code == 200
    assert res.json == []

    # Organisation filter: hepvs admin searching "Research" sees only the hepvs project
    res = client.get(
        url_for(
            "suggestions.completion",
            q="Research",
            field="metadata.name",
            resource="projects",
        )
    )
    assert res.status_code == 200
    assert res.json == ["HEPVS Research Project"]

    # Organisation filter: usi admin searching "Research" sees only the usi project
    login_user_via_session(client, email=user_usi["email"])
    res = client.get(
        url_for(
            "suggestions.completion",
            q="Research",
            field="metadata.name",
            resource="projects",
        )
    )
    assert res.status_code == 200
    assert res.json == ["USI Research Project"]

    # Users resource has no organisation filter — query by name prefix
    current_search.flush_and_refresh(index="users")
    login_user_via_session(client, email=user_hepvs["email"])
    res = client.get(url_for("suggestions.completion", q="Hepvs", field="full_name", resource="users"))
    assert res.status_code == 200
    assert res.json == ["Hepvsadmin Doe"]
