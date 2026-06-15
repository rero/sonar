# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Marshmallow export schema."""

from sonar.modules.users.serializers.schemas.export import ExportSchemaV1


def test_export_schema(user):
    """Test export schema."""
    result = ExportSchemaV1().dump(user)
    assert result["email"] == "orguser@rero.ch"
    assert result.get("password")
