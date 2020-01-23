# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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


@mock.patch(
    'sonar.modules.documents.tasks.DocumentRecord.get_record_by_identifier')
def test_import_records(mock_record_by_identifier, app, document_json_fixture,
                        bucket_location_fixture):
    """Test import records."""
    # Successful importing record
    mock_record_by_identifier.return_value = None
    document_json_fixture['files'] = [{
        'key': 'test.pdf',
        'url': 'http://some.url/file.pdf'
    }]
    import_records([document_json_fixture])
    assert DocumentRecord.get_record_by_pid('10000')

    # Error during importation of record
    def exception_side_effect(data):
        raise Exception("No record found for identifier")

    mock_record_by_identifier.side_effect = exception_side_effect
    document_json_fixture['pid'] = '10001'
    document_json_fixture['files'] = [{
        'key': 'test.pdf',
        'url': 'http://some.url/file.pdf'
    }]

    import_records([document_json_fixture])

    assert not DocumentRecord.get_record_by_pid('10001')
