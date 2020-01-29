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

"""Test SONAR api views."""

import json
import os

from invenio_app.factory import create_api

from sonar.theme.api_views import prepare_jsonschema

create_app = create_api


def test_prepare_jsonschema():
    """Test JSON schema transformation before returning by API endpoint."""
    with open(
            os.path.dirname(os.path.abspath(__file__)) +
            '/data/json_to_compile.json') as json_file:
        schema = json.load(json_file)
        assert '$schema' in schema
        assert 'pid' in schema['required']

        schema = prepare_jsonschema(schema)
        assert '$schema' not in schema
        assert 'pid' not in schema['required']


def test_json_schema_form(client):
    """Test JSON schema form api."""
    res = client.get('/schemaform/documents')
    assert res.status_code == 200

    res = client.get('/schemaform/not_existing')
    assert res.status_code == 404
