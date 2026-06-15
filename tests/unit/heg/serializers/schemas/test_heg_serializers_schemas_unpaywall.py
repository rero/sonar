# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Unpaywall schema."""

from sonar.heg.serializers.schemas.unpaywall import UnpaywallSchema


def test_unpaywall_schema(app):
    """Test Unpaysqll schema."""
    data = {
        "_id": "111",
        "oa_status": "green",
        "best_oa_location": {"url_for_pdf": "https://pdf.url"},
    }
    assert UnpaywallSchema().dump(data) == {
        "oa_status": "green",
        "files": [
            {
                "key": "fulltext.pdf",
                "label": "Full-text",
                "order": 0,
                "type": "file",
                "url": "https://pdf.url",
                "force_external_url": True,
            }
        ],
    }

    # Without images
    data = {"_id": "111", "oa_status": "green"}
    assert UnpaywallSchema().dump(data) == {"oa_status": "green"}
