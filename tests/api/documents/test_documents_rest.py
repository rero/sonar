# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test REST endpoint for documents."""

import json
import re
from copy import deepcopy

from flask import url_for
from invenio_accounts.testutils import login_user_via_session

from sonar.modules.documents.api import DocumentRecord


def test_get(client, document_with_file):
    """Get REST methods."""
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # created, updated
    for hit in res.json["hits"]["hits"]:
        assert "created" in hit
        assert "updated" in hit

    # the search results does not contains permissions
    fdata = res.json["hits"]["hits"][0]["metadata"]["_files"][0]
    assert list(fdata.keys()) == [
        "key",
        "label",
        "type",
        "order",
        "restriction",
        "links",
        "thumbnail",
    ]
    assert not fdata.get("permissions")

    # the item result should contains permissions
    res = client.get(url_for("invenio_records_rest.doc_item", pid_value=document_with_file["pid"]))
    assert res.status_code == 200
    assert res.json["metadata"]["_files"][0]["permissions"] == {
        "delete": False,
        "read": False,
        "update": False,
    }
    assert "ark" in [r["type"] for r in res.json["metadata"]["identifiedBy"]]

    # ark identifier is removed
    res = client.get(url_for("invenio_records_rest.doc_item", pid_value=document_with_file["pid"], format="rero"))
    assert res.status_code == 200
    assert "ark" not in [r["type"] for r in res.json["metadata"]["identifiedBy"]]

    # created, updated
    assert "created" in res.json
    assert "updated" in res.json


def test_post_put_delete(app, client, document_json, organisation):
    """Test putting metadata on existing file."""
    # Disable configuration
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    headers = [("Content-Type", "application/json")]
    data = deepcopy(document_json)
    data["organisation"] = [{"$ref": f"https://sonar.ch/api/organisations/{organisation['code']}"}]

    data["identifiedBy"].append({"type": "ark", "value": "ark:/99999/foo"})
    response = client.post(url_for("invenio_records_rest.doc_list"), headers=headers, data=json.dumps(data))
    assert response.status_code == 201
    data = response.json["metadata"]
    assert [r for r in data["identifiedBy"] if r["type"] == "ark"]
    doc = DocumentRecord.get_record_by_pid(data["pid"])
    assert doc.get_ark() != "ark:/99999/foo"

    response = client.put(
        url_for("invenio_records_rest.doc_item", pid_value=data["pid"]),
        headers=headers,
        data=json.dumps(data),
    )
    assert response.status_code == 200

    response = client.delete(url_for("invenio_records_rest.doc_item", pid_value=data["pid"]))
    assert response.status_code == 204
    response = client.get(url_for("invenio_records_rest.doc_item", pid_value=data["pid"]))

    assert response.status_code == 410
    data = deepcopy(document_json)
    data["organisation"] = [{"$ref": f"https://sonar.ch/api/organisations/{organisation['code']}"}]
    data.pop("identifiedBy", None)
    ark_scheme = app.config.pop("SONAR_APP_ARK_SCHEME", None)
    response = client.post(url_for("invenio_records_rest.doc_list"), headers=headers, data=json.dumps(data))
    assert response.status_code == 201
    client.delete(url_for("invenio_records_rest.doc_item", pid_value=response.json["metadata"]["pid"]))
    app.config["SONAR_APP_ARK_SCHEME"] = ark_scheme

    # assert document_with_file.get_ark()

    # # Retrieve document by doing a get request.
    # response = client.get(
    #     url_for("invenio_records_rest.doc_item", pid_value=document_with_file["pid"]),
    #     headers=headers,
    # )
    # data = response.json["metadata"]
    # # Put data to document
    # response = client.put(
    #     url_for("invenio_records_rest.doc_item", pid_value=document_with_file["pid"]),
    #     headers=headers,
    #     data=json.dumps(data),
    # )
    # assert response.status_code == 200

    # data["identifiedBy"].append({"type": "ark", "value": "ark:/99999/foo"})

    # # Put data to document
    # response = client.put(
    #     url_for("invenio_records_rest.doc_item", pid_value=document_with_file["pid"]),
    #     headers=headers,
    #     data=json.dumps(data),
    # )
    # from sonar.modules.documents.api import DocumentRecord
    # doc = DocumentRecord.get_record_by_pid(document_with_file["pid"])
    # assert doc.get_ark() == document_with_file.get_ark()
    # assert response.status_code == 200


def test_aggregations(app, client, document, superuser, admin):
    """Test aggregations."""
    # No context
    res = client.get(url_for("documents.aggregations"))
    assert res.json == [
        "document_type",
        "controlled_affiliation",
        "year",
        "collection",
        "language",
        "author",
        "subject",
        "organisation",
        "subdivision",
    ]

    # Collection view
    res = client.get(url_for("documents.aggregations", collection="coll"))
    assert res.json == [
        "document_type",
        "controlled_affiliation",
        "year",
        "language",
        "author",
        "subject",
        "organisation",
        "subdivision",
    ]

    # Dedicated view
    res = client.get(url_for("documents.aggregations", view="rero"))
    assert res.json == [
        "document_type",
        "controlled_affiliation",
        "year",
        "collection",
        "language",
        "author",
        "subject",
        "subdivision",
    ]

    # Global view
    res = client.get(url_for("documents.aggregations", view="global"))
    assert res.json == [
        "document_type",
        "controlled_affiliation",
        "year",
        "collection",
        "language",
        "author",
        "subject",
        "organisation",
    ]

    # Logged as superuser
    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("documents.aggregations"))
    assert res.json == [
        "document_type",
        "controlled_affiliation",
        "year",
        "collection",
        "language",
        "author",
        "subject",
        "organisation",
        "subdivision",
        {"key": "customField1", "name": "Test"},
    ]

    # Logged as admin
    login_user_via_session(client, email=admin["email"])
    res = client.get(url_for("documents.aggregations"))
    assert res.json == [
        "document_type",
        "controlled_affiliation",
        "year",
        "collection",
        "language",
        "author",
        "subject",
        "subdivision",
        {"key": "customField1", "name": "Test"},
    ]


def test_export_invalid_format(client, document):
    """Unsupported format returns 400."""
    res = client.get(url_for("documents.export", pid_value=document["pid"], fmt="unknown"))
    assert res.status_code == 400
    assert "format" in res.json["message"].lower()


def test_export_not_found(db, client):
    """Unknown pid returns 404 for export."""
    res = client.get(url_for("documents.export", pid_value="unknown-pid", fmt="json"))
    assert res.status_code == 404


def _assert_export_filename(headers, pid, extension):
    """Assert Content-Disposition contains a dated filename."""
    assert re.search(rf"\d{{8}}-{re.escape(pid)}{re.escape(extension)}", headers["Content-Disposition"])


def test_export_json(client, document):
    """JSON export returns attachment with .json extension."""
    res = client.get(url_for("documents.export", pid_value=document["pid"], fmt="json"))
    assert res.status_code == 200
    assert res.content_type == "application/json"
    _assert_export_filename(res.headers, document["pid"], ".json")


def test_export_bibtex(client, document):
    """BibTeX export returns attachment with .bib extension."""
    res = client.get(url_for("documents.export", pid_value=document["pid"], fmt="bibtex"))
    assert res.status_code == 200
    assert res.content_type == "application/x-bibtex"
    _assert_export_filename(res.headers, document["pid"], ".bib")
    assert "@" in res.data.decode()


def test_export_ris(client, document):
    """RIS export returns attachment with .ris extension."""
    res = client.get(url_for("documents.export", pid_value=document["pid"], fmt="ris"))
    assert res.status_code == 200
    assert res.content_type == "application/x-research-info-systems"
    _assert_export_filename(res.headers, document["pid"], ".ris")
    assert "TY  -" in res.data.decode()


def test_export_dc(client, document):
    """Dublin Core export returns attachment with .xml extension."""
    res = client.get(url_for("documents.export", pid_value=document["pid"], fmt="dc"))
    assert res.status_code == 200
    assert res.content_type.startswith("text/xml")
    _assert_export_filename(res.headers, document["pid"], ".xml")


def test_export_sanitizes_filename(client, make_document):
    """Content-Disposition filename is sanitized from unsafe pid characters."""
    doc = make_document(organisation="org", pid='foo"; evil')
    res = client.get(url_for("documents.export", pid_value=doc["pid"], fmt="json"))
    assert res.status_code == 200
    disposition = res.headers["Content-Disposition"]
    assert '"' not in disposition.split("filename=", 1)[1]
    assert ";" not in disposition.split("filename=", 1)[1]
