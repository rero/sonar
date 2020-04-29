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

import mock
from flask import url_for
from utils import VerifyRecordPermissionPatch


@mock.patch('invenio_records_rest.views.verify_record_permission',
            mock.MagicMock(return_value=VerifyRecordPermissionPatch))
def test_simple_flow(client, document_json_fixture):
    """Test simple flow using REST API."""
    headers = [('Content-Type', 'application/json')]

    # create a record
    response = client.post(url_for('invenio_records_rest.doc_list'),
                           data=json.dumps(document_json_fixture),
                           headers=headers)
    assert response.status_code == 201

    # retrieve record
    res = client.get(url_for('invenio_records_rest.doc_item', pid_value=1))
    assert res.status_code == 200
    assert response.json['metadata']['title'][0]['mainTitle'][0][
        'value'] == 'Title of the document'


def test_add_files_restrictions(client, document_with_file):
    """Test adding file restrictions before dumping object."""
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=10000, resolve=1))
    assert res.status_code == 200
    assert res.json['metadata']['_files'][0]['restriction'] == {
        'restricted': True,
        'date': '2021-01-01'
    }
