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

"""Test documents permissions."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(client, make_document, superuser, admin, moderator, submitter,
              user):
    """Test list documents permissions."""
    make_document(None)
    make_document('org')

    # Not logged
    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 2

    # Public search
    res = client.get(url_for('invenio_records_rest.doc_list', view='sonar'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 2

    # Public search for organisation
    res = client.get(url_for('invenio_records_rest.doc_list', view='org'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1


def test_create(client, document_json, superuser, admin, moderator, submitter,
                user):
    """Test create documents permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.post(url_for('invenio_records_rest.doc_list'),
                      data=json.dumps(document_json),
                      headers=headers)
    assert res.status_code == 401

    # User
    login_user_via_session(client, email=user['email'])
    res = client.post(url_for('invenio_records_rest.doc_list'),
                      data=json.dumps(document_json),
                      headers=headers)
    assert res.status_code == 403

    # submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.post(url_for('invenio_records_rest.doc_list'),
                      data=json.dumps(document_json),
                      headers=headers)
    assert res.status_code == 403

    # Moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.post(url_for('invenio_records_rest.doc_list'),
                      data=json.dumps(document_json),
                      headers=headers)
    assert res.status_code == 201
    assert res.json['metadata']['organisation'][
        '$ref'] == 'https://sonar.ch/api/organisations/org'

    # Admin
    login_user_via_session(client, email=admin['email'])
    res = client.post(url_for('invenio_records_rest.doc_list'),
                      data=json.dumps(document_json),
                      headers=headers)
    assert res.status_code == 201
    assert res.json['metadata']['organisation'][
        '$ref'] == 'https://sonar.ch/api/organisations/org'

    # Super user
    login_user_via_session(client, email=superuser['email'])
    res = client.post(url_for('invenio_records_rest.doc_list'),
                      data=json.dumps(document_json),
                      headers=headers)
    assert res.status_code == 201
    assert res.json['metadata']['organisation'][
        '$ref'] == 'https://sonar.ch/api/organisations/org'


def test_read(client, document, make_user, superuser, admin, moderator,
              submitter, user):
    """Test read documents permissions."""
    # Not logged
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': False,
        'read': True,
        'update': True
    }

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': True,
        'read': True,
        'update': True
    }

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': True,
        'read': True,
        'update': True
    }


def test_update(client, document, make_user, superuser, admin, moderator,
                submitter, user):
    """Test update documents permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.put(url_for('invenio_records_rest.doc_item',
                             pid_value=document['pid']),
                     data=json.dumps(document.dumps()),
                     headers=headers)
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.put(url_for('invenio_records_rest.doc_item',
                             pid_value=document['pid']),
                     data=json.dumps(document.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.put(url_for('invenio_records_rest.doc_item',
                             pid_value=document['pid']),
                     data=json.dumps(document.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.put(url_for('invenio_records_rest.doc_item',
                             pid_value=document['pid']),
                     data=json.dumps(document.dumps()),
                     headers=headers)
    assert res.status_code == 200

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.put(url_for('invenio_records_rest.doc_item',
                             pid_value=document['pid']),
                     data=json.dumps(document.dumps()),
                     headers=headers)
    assert res.status_code == 200

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.put(url_for('invenio_records_rest.doc_item',
                             pid_value=document['pid']),
                     data=json.dumps(document.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.doc_item',
                             pid_value=document['pid']),
                     data=json.dumps(document.dumps()),
                     headers=headers)
    assert res.status_code == 200


def test_delete(client, document, make_document, make_user, superuser, admin,
                moderator, submitter, user):
    """Test delete documents permissions."""
    # Not logged
    res = client.delete(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.delete(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.delete(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.delete(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 204

    # Create a new document
    document = make_document()

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.delete(
        url_for('invenio_records_rest.doc_item', pid_value=document['pid']))
    assert res.status_code == 204
