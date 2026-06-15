# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test client views for PDF extractor."""

from invenio_accounts.testutils import login_user_via_view


def test_pdf_extractor_test_page(client, user):
    """Test the PDF extractor test page."""
    login_user_via_view(client, email=user["email"], password="123456")

    response = client.get("/pdf-extractor/test")
    assert response.status_code == 200
    assert "PDF metadata extraction" in str(response.data)
