# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test client views for PDF extractor."""

from invenio_accounts.testutils import login_user_via_session


def test_pdf_extractor_test_page(client, user, submitter):
    """Test the PDF extractor test page."""
    # A submitter is required.
    assert client.get("/pdf-extractor/test").status_code == 401

    login_user_via_session(client, email=user["email"])
    assert client.get("/pdf-extractor/test").status_code == 403

    login_user_via_session(client, email=submitter["email"])
    response = client.get("/pdf-extractor/test")
    assert response.status_code == 200
    assert "PDF metadata extraction" in str(response.data)
