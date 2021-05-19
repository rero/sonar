# -*- coding: utf-8 -*-
#
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

"""Test documents JSON schema."""

from sonar.json_schemas.documents_json_schema import DocumentsJSONSchema


def test_process(app, monkeypatch):
    """Test process."""
    schema = DocumentsJSONSchema('documents')
    result = schema.get_schema()
    assert result['properties']['customField1']['title'] == 'Custom field 1'

    # No current organisation
    schema = DocumentsJSONSchema('documents')
    result = schema.process()
    assert not result['properties'].get('customField1')

    # Custom label for field
    monkeypatch.setattr(
        'sonar.json_schemas.documents_json_schema.current_organisation', {
            'isDedicated': True,
            'documentsCustomField1': {
                'label': [{
                    'language': 'eng',
                    'value': 'Test'
                }]
            }
        })

    schema = DocumentsJSONSchema('documents')
    result = schema.process()
    assert result['properties']['customField1']['title'] == 'Test'
