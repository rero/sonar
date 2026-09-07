# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test api views for PDF extractor."""

import json
from io import BytesIO

from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api

create_app = create_api


def test_metadata(client, user, submitter, pdf_file, mock_grobid_response):
    """Test metadata extraction."""
    # A submitter is required.
    assert client.post("/pdf-extractor/metadata").status_code == 401
    login_user_via_session(client, email=user["email"])
    assert client.post("/pdf-extractor/metadata").status_code == 403

    login_user_via_session(client, email=submitter["email"])

    response = client.post("/pdf-extractor/metadata")
    assert response.status_code == 400

    with open(pdf_file, "rb") as file:
        content = file.read()

    data = {"file": (BytesIO(content), "test.pdf")}

    response = client.post("/pdf-extractor/metadata", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "teiHeader" in result

    title = result["teiHeader"]["fileDesc"]["titleStmt"]["title"]["#text"]
    assert title[:10] == "High-harmo"


def test_full_text(client, user, submitter, pdf_file):
    """Test full text extraction."""
    # A submitter is required.
    assert client.post("/pdf-extractor/full-text").status_code == 401
    login_user_via_session(client, email=user["email"])
    assert client.post("/pdf-extractor/full-text").status_code == 403

    login_user_via_session(client, email=submitter["email"])

    response = client.post("/pdf-extractor/full-text")
    assert response.status_code == 400

    with open(pdf_file, "rb") as file:
        content = file.read()

    data = {"file": (BytesIO(content), "test.pdf")}

    response = client.post("/pdf-extractor/full-text", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "text" in result
