# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test JSON schema."""

import pytest

from sonar.jsonschemas.json_schema_base import JSONSchemaBase


def test_load(app, monkeypatch):
    """Test load."""
    # Non existing schema
    with pytest.raises(Exception) as exception:
        schema = JSONSchemaBase("fakes")
        assert str(exception.value) == 'Schema "fakes/fake-v1.0.0.json" not found'

    # Standard schema
    schema = JSONSchemaBase("documents")
    assert schema.get_schema()["title"] == "Document"

    schema = JSONSchemaBase("projects")
    assert "hepvs" not in schema.get_schema()["id"]

    # Schema for custom resource
    monkeypatch.setattr("sonar.jsonschemas.json_schema_base.current_organisation", {"code": "hepvs"})
    schema = JSONSchemaBase("projects")
    assert "hepvs" in schema.get_schema()["id"]
