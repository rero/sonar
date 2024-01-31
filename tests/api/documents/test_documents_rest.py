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

"""Test REST endpoint for documents."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_get(client, document_with_file):
    """Get REST methods."""
    res = client.get(url_for('invenio_records_rest.doc_list', view='global'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1
    # the search results does not contains permissions
    fdata = res.json['hits']['hits'][0]['metadata']['_files'][0]
    assert list(fdata.keys()) == [
        'key', 'label', 'type', 'order', 'restriction', 'links', 'thumbnail'
    ]
    assert not fdata.get("permissions")

    # the item result should contains permissions
    res = client.get(url_for('invenio_records_rest.doc_item', pid_value=document_with_file['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['_files'][0]['permissions'] == {
        'delete': False, 'read': False,'update': False}


def test_put(app, client, document_with_file):
    """Test putting metadata on existing file."""
    # Disable configuration
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    headers = [('Content-Type', 'application/json')]

    # Retrieve document by doing a get request.
    response = client.get(url_for('invenio_records_rest.doc_item',
                                  pid_value=document_with_file['pid']),
                          headers=headers)

    # Put data to document
    response = client.put(url_for('invenio_records_rest.doc_item',
                                  pid_value=document_with_file['pid']),
                          headers=headers,
                          data=json.dumps(response.json['metadata']))
    assert response.status_code == 200


def test_aggregations(app, client, document, superuser, admin):
    """Test aggregations."""
    # No context
    res = client.get(url_for('documents.aggregations'))
    assert res.json == [
        'document_type', 'controlled_affiliation', 'year', 'collection',
        'language', 'author', 'subject', 'organisation', 'subdivision'
    ]

    # Collection view
    res = client.get(url_for('documents.aggregations', collection='coll'))
    assert res.json == [
        'document_type', 'controlled_affiliation', 'year', 'language',
        'author', 'subject', 'organisation', 'subdivision'
    ]

    # Dedicated view
    res = client.get(url_for('documents.aggregations', view='rero'))
    assert res.json == [
        'document_type', 'controlled_affiliation', 'year', 'collection',
        'language', 'author', 'subject', 'subdivision'
    ]

    # Global view
    res = client.get(url_for('documents.aggregations', view='global'))
    assert res.json == [
        'document_type', 'controlled_affiliation', 'year', 'collection',
        'language', 'author', 'subject', 'organisation'
    ]

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('documents.aggregations'))
    assert res.json == [
        'document_type', 'controlled_affiliation', 'year', 'collection',
        'language', 'author', 'subject', 'organisation', 'subdivision', {
            'key': 'customField1',
            'name': 'Test'
        }
    ]

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('documents.aggregations'))
    assert res.json == [
        'document_type', 'controlled_affiliation', 'year', 'collection',
        'language', 'author', 'subject', 'subdivision', {
            'key': 'customField1',
            'name': 'Test'
        }
    ]
