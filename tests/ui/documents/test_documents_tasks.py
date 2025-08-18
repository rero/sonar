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

"""Test documents tasks."""

import mock

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.tasks import import_records


@mock.patch("sonar.modules.documents.api.DocumentRecord.get_record_by_identifier")
def test_import_records(mock_record_by_identifier, app, document_json, bucket_location):
    """Test import records."""
    files = [{"key": "test.pdf", "url": "http://some.url/file.pdf"}]

    # Successful importing record
    mock_record_by_identifier.return_value = None
    document_json["files"] = files
    ids = import_records([document_json])
    record = DocumentRecord.get_record(ids[0])
    assert record
    assert record["harvested"]

    # Update
    mock_record_by_identifier.return_value = record
    ids = import_records([document_json])
    assert DocumentRecord.get_record(ids[0])

    # Error during importation of record
    def exception_side_effect(data):
        raise Exception("No record found for identifier")

    mock_record_by_identifier.side_effect = exception_side_effect

    ids = import_records([document_json])

    assert not ids
