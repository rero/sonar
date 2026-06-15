# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test schema.org marshmallow schema."""

from sonar.modules.documents.marshmallow import DocumentMetadataSchemaV1
from sonar.modules.documents.marshmallow.json import ThumbnailSchemaV1


def test_partof(document):
    """Test partOf serialization."""
    document = {
        "pid": "1",
        "organisation": [{"$ref": "https://sonar.rero.ch/api/organisations/org"}],
        "partOf": [{"document": {"title": "Host document", "contribution": ["Muller"]}}],
    }
    assert DocumentMetadataSchemaV1().dump(document)["partOf"][0]["document"]["contribution"] == ["Muller"]


def test_file_key():
    """Test that the key encoding has not be changed."""
    file_name = "testé.pdf"
    assert ThumbnailSchemaV1().load({"key": file_name})["key"] == file_name
