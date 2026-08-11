# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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


def test_completion_array_field(client, document_json, make_document, make_user, search_clear):
    """Test completion suggestions on a field nested in an array."""
    document_json["contribution"] = [
        {
            "agent": {"type": "bf:Person", "preferred_name": "Dupont, Jean"},
            "role": ["cre"],
        },
        {
            "agent": {"type": "bf:Person", "preferred_name": "Zimmermann, Ada"},
            "role": ["cre"],
        },
    ]
    make_document(organisation="org")
    current_search.flush_and_refresh(index="documents")

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])

    field = "contribution.agent.preferred_name.suggest"

    # A partial word is enough, the whole word is not required
    for query in ["D", "Dup", "dupont", "Dupont, Jean"]:
        res = client.get(url_for("suggestions.completion", q=query, field=field, resource="documents"))
        assert res.status_code == 200
        assert res.json == ["Dupont, Jean"]

    # A matching record does not suggest the other values of its field
    res = client.get(url_for("suggestions.completion", q="Zim", field=field, resource="documents"))
    assert res.status_code == 200
    assert res.json == ["Zimmermann, Ada"]

    # Unknown value
    res = client.get(url_for("suggestions.completion", q="Nobody", field=field, resource="documents"))
    assert res.status_code == 200
    assert res.json == []
