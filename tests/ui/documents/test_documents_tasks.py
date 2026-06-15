# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test documents tasks."""

from unittest import mock

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
