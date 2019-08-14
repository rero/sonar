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

"""Test simple rest flow."""

import json

from invenio_search import current_search


def test_simple_flow(client):
    """Test simple flow using REST API."""
    headers = [('Content-Type', 'application/json')]
    data = {
        'title': 'The title of the record',
        'abstracts': [
            {'language': 'fre', 'value': 'Record summary'}
        ],
    }
    url = 'https://localhost:5000/documents/'

    # create a record
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.status_code == 201
    current_search.flush_and_refresh('documents')

    # retrieve record
    res = client.get('https://localhost:5000/documents/1')
    assert res.status_code == 200
