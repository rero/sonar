# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test schema.org marshmallow schema."""

from sonar.modules.documents.marshmallow import DocumentMetadataSchemaV1
from sonar.modules.documents.marshmallow.json import ThumbnailSchemaV1


def test_partOf(document):
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
    assert ThumbnailSchemaV1().load(dict(key=file_name))["key"] == file_name
