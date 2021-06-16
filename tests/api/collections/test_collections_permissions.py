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

"""Test collections permissions."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, client, make_organisation, make_collection, superuser,
              admin, moderator, submitter, user):
    """Test list collections permissions."""
    make_organisation('org2')
    make_collection('org')
    make_collection('org2')

    # Not logged
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 401

    # Not logged but permission checks disabled
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 2
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 2


def test_create(client, superuser, admin, moderator, submitter, user):
    """Test create collections permissions."""
    data = {'name': [{'language': 'eng', 'value': 'Name'}]}

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.post(url_for('invenio_records_rest.coll_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 401

    # User
    login_user_via_session(client, email=user['email'])
    res = client.post(url_for('invenio_records_rest.coll_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 403

    # submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.post(url_for('invenio_records_rest.coll_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 403

    # Moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.post(url_for('invenio_records_rest.coll_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 403

    # Admin
    login_user_via_session(client, email=admin['email'])
    res = client.post(url_for('invenio_records_rest.coll_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 201

    # Super user
    login_user_via_session(client, email=superuser['email'])
    res = client.post(url_for('invenio_records_rest.coll_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 201


def test_read(client, make_organisation, make_collection, superuser, admin,
              moderator, submitter, user):
    """Test read collections permissions."""
    make_organisation('org2')
    collection1 = make_collection('org')
    collection2 = make_collection('org2')

    # Not logged
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection1['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection1['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection1['pid']))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection1['pid']))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection1['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': True,
        'read': True,
        'update': True
    }

    # Logged as admin of other organisation
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection2['pid']))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection1['pid']))
    assert res.status_code == 200

    login_user_via_session(client, email=superuser['email'])
    res = client.get(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection2['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': True,
        'read': True,
        'update': True
    }


def test_update(client, make_organisation, make_collection, superuser, admin,
                moderator, submitter, user):
    """Test update collections permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    make_organisation('org2')
    collection1 = make_collection('org')
    collection2 = make_collection('org2')

    # Not logged
    res = client.put(url_for('invenio_records_rest.coll_item',
                             pid_value=collection1['pid']),
                     data=json.dumps(collection1.dumps()),
                     headers=headers)
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.put(url_for('invenio_records_rest.coll_item',
                             pid_value=collection1['pid']),
                     data=json.dumps(collection1.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.put(url_for('invenio_records_rest.coll_item',
                             pid_value=collection1['pid']),
                     data=json.dumps(collection1.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.put(url_for('invenio_records_rest.coll_item',
                             pid_value=collection1['pid']),
                     data=json.dumps(collection1.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.put(url_for('invenio_records_rest.coll_item',
                             pid_value=collection1['pid']),
                     data=json.dumps(collection1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    # Logged as admin of other organisation
    res = client.put(url_for('invenio_records_rest.coll_item',
                             pid_value=collection2['pid']),
                     data=json.dumps(collection2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.coll_item',
                             pid_value=collection1['pid']),
                     data=json.dumps(collection1.dumps()),
                     headers=headers)
    assert res.status_code == 200


def test_delete(client, db, document, collection, make_organisation,
                make_collection, superuser, admin, moderator, submitter, user):
    """Test delete collections permissions."""
    # Not logged
    res = client.delete(
        url_for('invenio_records_rest.coll_item', pid_value=collection['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.delete(
        url_for('invenio_records_rest.coll_item', pid_value=collection['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.delete(
        url_for('invenio_records_rest.coll_item', pid_value=collection['pid']))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.delete(
        url_for('invenio_records_rest.coll_item', pid_value=collection['pid']))
    assert res.status_code == 403

    make_organisation('org2')
    collection2 = make_collection('org2')

    # Cannot remove collection from other organisation
    res = client.delete(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection2['pid']))
    assert res.status_code == 403

    collection = make_collection('org')

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.coll_item', pid_value=collection['pid']))
    assert res.status_code == 204

    collection = make_collection('org')

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.delete(
        url_for('invenio_records_rest.coll_item', pid_value=collection['pid']))
    assert res.status_code == 204

    # Can remove any collection
    login_user_via_session(client, email=superuser['email'])
    res = client.delete(
        url_for('invenio_records_rest.coll_item',
                pid_value=collection2['pid']))
    assert res.status_code == 204

    collection = make_collection('org')

    # Cannot remove collection as it is linked to document.
    document['collections'] = [{
        '$ref':
        'https://sonar.ch/api/collections/{pid}'.format(pid=collection['pid'])
    }]
    document.commit()
    db.session.commit()
    document.reindex()

    res = client.delete(
        url_for('invenio_records_rest.coll_item', pid_value=collection['pid']))
    assert res.status_code == 403
