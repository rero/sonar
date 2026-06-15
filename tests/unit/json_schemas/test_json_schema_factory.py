# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test JSON schema factory."""

from sonar.jsonschemas.deposits_json_schema import DepositsJSONSchema
from sonar.jsonschemas.factory import JSONSchemaFactory
from sonar.jsonschemas.json_schema_base import JSONSchemaBase


def test_create(app):
    """Test schema object creation."""
    # No custom schema
    schema = JSONSchemaFactory.create("organisations")
    assert isinstance(schema, JSONSchemaBase)

    # Specific schema
    schema = JSONSchemaFactory.create("deposits")
    assert isinstance(schema, DepositsJSONSchema)
