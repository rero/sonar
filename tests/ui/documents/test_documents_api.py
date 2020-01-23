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

"""Test documents API."""

from sonar.modules.documents.api import DocumentRecord


def test_get_record_by_identifier(app, document_fixture):
    """Test getting record by its identifier."""
    # Record found
    record = DocumentRecord.get_record_by_identifier([{
        'value': 'oai:doc.rero.ch:20050302172954-WU',
        'type': 'bf:Identifier'
    }])
    assert record['pid'] == '10000'

    # Record not found
    record = DocumentRecord.get_record_by_identifier([{
        'value': 'oai:unknown',
        'type': 'bf:Identifier'
    }])
    assert not record
