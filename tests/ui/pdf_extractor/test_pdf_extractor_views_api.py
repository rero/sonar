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

"""Test api views for PDF extractor."""

import json
from io import BytesIO

from invenio_app.factory import create_api

create_app = create_api


def test_metadata(client, pdf_file, mock_grobid_response):
    """Test metadata extraction."""
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


def test_full_text(client, pdf_file):
    """Test full text extraction."""
    response = client.post("/pdf-extractor/full-text")
    assert response.status_code == 400

    with open(pdf_file, "rb") as file:
        content = file.read()

    data = {"file": (BytesIO(content), "test.pdf")}

    response = client.post("/pdf-extractor/full-text", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "text" in result
