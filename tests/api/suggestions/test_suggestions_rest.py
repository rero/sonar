# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test suggestions rest."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from invenio_search import current_search, current_search_client


def completion(client, query, field, resource="documents"):
    """Call the completion endpoint and return the suggestions.

    :param client: test client.
    :param query: query typed by the user.
    :param field: field, or comma separated list of fields, to suggest from.
    :param resource: resource to search in.
    :returns: the suggested values.
    """
    res = client.get(url_for("suggestions.completion", q=query, field=field, resource=resource))
    assert res.status_code == 200

    return res.json


def contributions(*names):
    """Build contributions for the given preferred names.

    :param names: preferred names of the contributors.
    :returns: list of contributions.
    """
    return [{"agent": {"type": "bf:Person", "preferred_name": name}, "role": ["cre"]} for name in names]


def test_completion_params(client, make_user, user_without_role):
    """Test access control and parameters validation."""
    # 401: unauthenticated request blocked before parameter validation
    res = client.get(url_for("suggestions.completion"))
    assert res.status_code == 401

    # 403: authenticated but no submitter role
    login_user_via_session(client, email=user_without_role.email)
    res = client.get(url_for("suggestions.completion", q="test", field="customField1", resource="documents"))
    assert res.status_code == 403

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])

    # No query parameter
    res = client.get(url_for("suggestions.completion"))
    assert res.status_code == 400
    assert res.json == {"error": "No query parameter given"}

    # No field parameter
    res = client.get(url_for("suggestions.completion", q="test"))
    assert res.status_code == 400
    assert res.json == {"error": "No field parameter given"}

    # No resource parameter
    res = client.get(url_for("suggestions.completion", q="test", field="customField1"))
    assert res.status_code == 400
    assert res.json == {"error": "No resource parameter given"}

    # Non-existent resource
    res = client.get(url_for("suggestions.completion", q="test", field="customField1", resource="unknown"))
    assert res.status_code == 404
    assert res.json == {"error": "Search class not found"}


def test_completion_resource_without_suggestions(client, make_user, search_clear):
    """Test a resource that does not index suggestable values."""
    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])
    current_search.flush_and_refresh(index="users")

    # The record is indexed, but only the denormalized values can be suggested
    assert completion(client, user["email"], "email", "users") == []


def test_completion_documents(client, document_json, make_document, make_user, search_clear):
    """Test completion suggestions on documents."""
    # `customField1` is `["Test"]` in the fixture
    document_json["contribution"] = contributions("Dupont, Jean", "Zimmermann, Ada", "Testeur, Léa")
    make_document(organisation="org")
    current_search.flush_and_refresh(index="documents")

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])

    field = "contribution.agent.preferred_name"

    # A partial word is enough, the whole word is not required
    for query in ["D", "Dup", "dupont", "Dupont, Jean"]:
        assert completion(client, query, field) == ["Dupont, Jean"]

    # A matching record does not suggest the other values of its field
    assert completion(client, "Zim", field) == ["Zimmermann, Ada"]

    # Each typed word must match the same value, not the same record
    assert completion(client, "Dupont Ada", field) == []

    # Values of several fields in a single request
    assert completion(client, "te", f"{field},customField1") == ["Test", "Testeur, Léa"]

    # Unknown value and unknown field
    assert completion(client, "Nobody", field) == []
    assert completion(client, "Dupont", "unknown") == []


def test_completion_documents_diacritics(client, document_json, make_document, make_user, search_clear):
    """Test completion suggestions with folded values and queries."""
    document_json["contribution"] = contributions("Délèze, Sébastien", "Müller, Anaïs")
    make_document(organisation="org")
    current_search.flush_and_refresh(index="documents")

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])

    field = "contribution.agent.preferred_name"

    # Diacritics are folded on both sides
    assert completion(client, "dele", field) == ["Délèze, Sébastien"]
    assert completion(client, "Délè", field) == ["Délèze, Sébastien"]

    # The German transliteration is folded too
    assert completion(client, "mueller", field) == ["Müller, Anaïs"]
    assert completion(client, "Müll", field) == ["Müller, Anaïs"]


def test_completion_documents_long_words(client, document_json, make_document, make_user, search_clear):
    """Test completion suggestions on words longer than the indexed n-grams."""
    name = "Rechtsschutzversicherungsgesellschaft, Anna"
    document_json["contribution"] = contributions(name)
    make_document(organisation="org")
    current_search.flush_and_refresh(index="documents")

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])

    field = "contribution.agent.preferred_name"

    # The `autocomplete` analyzer only indexes the 30 first characters of a
    # word, the query is truncated to match them
    assert completion(client, "Rechtsschutzversicherungsgesel", field) == [name]
    assert completion(client, "Rechtsschutzversicherungsgesellschaft", field) == [name]


def test_completion_documents_frequency(client, document_json, make_document, make_user, search_clear):
    """Test that a frequent value does not hide the rare ones."""
    # More records than the 20 the previous implementation looked at
    document_json["contribution"] = contributions("Common, Value")
    for _ in range(21):
        make_document(organisation="org")

    document_json["contribution"] = contributions("Comte, Rare")
    make_document(organisation="org")
    current_search.flush_and_refresh(index="documents")

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])

    # Values are ordered by the number of records they appear in
    assert completion(client, "co", "contribution.agent.preferred_name") == ["Common, Value", "Comte, Rare"]


def test_completion_documents_max_results(client, document_json, make_document, make_user, search_clear):
    """Test that the suggestions of a single record are limited."""
    document_json["contribution"] = contributions(*[f"Auteur {index:02d}" for index in range(25)])
    make_document(organisation="org")
    current_search.flush_and_refresh(index="documents")

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])

    assert len(completion(client, "auteur", "contribution.agent.preferred_name")) == 20


def test_completion_documents_organisation(
    client, document_json, make_document, make_organisation, make_user, superuser, search_clear
):
    """Test the organisation filter on documents."""
    document_json["contribution"] = contributions("Dupont, Jean")
    make_document(organisation="org")

    # The factory forces the `org` reference, set the second organisation by hand
    make_organisation("org2")
    document_json["contribution"] = contributions("Duvernay, Claire")
    document_json["organisation"] = [{"$ref": "https://sonar.ch/api/organisations/org2"}]
    make_document(organisation=None)

    current_search.flush_and_refresh(index="documents")

    field = "contribution.agent.preferred_name"

    user = make_user("admin", organisation="org")
    login_user_via_session(client, email=user["email"])
    assert completion(client, "du", field) == ["Dupont, Jean"]

    user_org2 = make_user("admin", organisation="org2")
    login_user_via_session(client, email=user_org2["email"])
    assert completion(client, "du", field) == ["Duvernay, Claire"]

    # Superusers are not restricted to their organisation
    login_user_via_session(client, email=superuser["email"])
    assert completion(client, "du", field) == ["Dupont, Jean", "Duvernay, Claire"]


def test_completion_projects(client, project_hepvs_json, make_user, search_clear):
    """Test completion suggestions on projects."""
    # `projectSponsor` is "Sébastien Délèze" and `innerSearcher` ["John Doe"]
    user_hepvs = make_user("admin", organisation="hepvs", organisation_is_shared=False, access="admin-access")
    login_user_via_session(client, email=user_hepvs["email"])

    project_hepvs_json["metadata"]["organisation"] = {"$ref": "https://sonar.ch/api/organisations/hepvs"}
    project_hepvs_json["metadata"]["user"] = {"$ref": f"https://sonar.ch/api/users/{user_hepvs['pid']}"}
    res = client.post(
        url_for("projects.search"),
        data=json.dumps(project_hepvs_json),
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 201

    current_search.flush_and_refresh(index="projects")

    fields = "metadata.projectSponsor,metadata.innerSearcher"

    # A single request covers each of the requested fields
    assert completion(client, "dele", fields, "projects") == ["Sébastien Délèze"]
    assert completion(client, "doe", fields, "projects") == ["John Doe"]
    assert completion(client, "te", "metadata.keywords", "projects") == ["Test"]

    # The suggestions are not part of the stored source
    hit = current_search_client.search(index="projects")["hits"]["hits"][0]
    assert "suggestions" not in hit["_source"]

    # Organisation filter: another organisation gets no suggestion
    user_usi = make_user("admin", organisation="usi", access="admin-access")
    login_user_via_session(client, email=user_usi["email"])
    assert completion(client, "dele", fields, "projects") == []
