# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Marshmallow export schema."""

from io import BytesIO

from sonar.modules.organisations.serializers.schemas.export import ExportSchemaV1


def test_export_schema(organisation):
    """Test export schema."""
    organisation.files["logo.jpg"] = BytesIO(b"File content")
    result = ExportSchemaV1().dump(organisation)
    assert result["code"] == "org"
    assert len(result["files"]) == 1
    assert result["files"][0]["key"] == "logo.jpg"
    assert result["files"][0].get("uri")
