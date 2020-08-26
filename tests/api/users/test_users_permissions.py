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

"""Test users permissions."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, client, make_user, superuser, admin, moderator, submitter,
              user):
    """Test list users permissions."""
    make_user('user', 'org2')

    # Not logged
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 401

    # Not logged but permission checks disabled
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 6
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)

    # # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1

    # Test search email, no result
    res = client.get(
        url_for('invenio_records_rest.user_list',
                q='email:test@gmail.com NOT pid:orguser'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 0

    # Test search email, existing email
    res = client.get(
        url_for('invenio_records_rest.user_list',
                q='email:orgadmin@rero.ch NOT pid:orguser'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1
    assert not res.json['hits']['hits'][0]['metadata'].get('email')

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 4

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 6


def test_create(client, organisation, superuser, admin, moderator, submitter,
                user):
    """Test create users permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    user_json = {
        'email': 'user@rero.ch',
        'full_name': 'User',
        'role': 'user'
    }

    # Not logged
    res = client.post(url_for('invenio_records_rest.user_list'),
                      data=json.dumps(user_json),
                      headers=headers)
    assert res.status_code == 401

    # User
    login_user_via_session(client, email=user['email'])
    res = client.post(url_for('invenio_records_rest.user_list'),
                      data=json.dumps(user_json),
                      headers=headers)
    assert res.status_code == 403

    # submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.post(url_for('invenio_records_rest.user_list'),
                      data=json.dumps(user_json),
                      headers=headers)
    assert res.status_code == 403

    # Moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.post(url_for('invenio_records_rest.user_list'),
                      data=json.dumps(user_json),
                      headers=headers)
    assert res.status_code == 403

    # Admin
    login_user_via_session(client, email=admin['email'])
    res = client.post(url_for('invenio_records_rest.user_list'),
                      data=json.dumps(user_json),
                      headers=headers)
    assert res.status_code == 201
    assert res.json['metadata']['organisation'][
        '$ref'] == 'https://sonar.ch/api/organisations/org'

    # Super user
    user_json['organisation'] = {
        '$ref':
        'https://sonar.ch/api/organisations/{organisation}'.format(
            organisation=organisation['pid'])
    }

    login_user_via_session(client, email=superuser['email'])
    res = client.post(url_for('invenio_records_rest.user_list'),
                      data=json.dumps(user_json),
                      headers=headers)
    assert res.status_code == 201
    assert res.json['metadata']['organisation'][
        '$ref'] == 'https://sonar.ch/api/organisations/org'


def test_read(client, make_user, superuser, admin, moderator, submitter, user):
    """Test read users permissions."""
    # Not logged
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 401

    # Logged as user and read himself
    login_user_via_session(client, email=user['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': False,
        'read': True,
        'update': True
    }

    # Logged as user and read other
    login_user_via_session(client, email=user['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=moderator['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=submitter['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': False,
        'read': True,
        'update': True
    }

    login_user_via_session(client, email=submitter['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=moderator['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': False,
        'read': True,
        'update': True
    }

    login_user_via_session(client, email=moderator['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': True,
        'read': True,
        'update': True
    }

    # Logged as admin, try to read superuser
    login_user_via_session(client, email=admin['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=superuser['pid']))
    assert res.status_code == 403

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': True,
        'read': True,
        'update': True
    }


def test_update(client, make_user, superuser, admin, moderator, submitter,
                user):
    """Test update users permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=user['pid']),
                     data=json.dumps(user.dumps()),
                     headers=headers)
    assert res.status_code == 401

    # Logged as user and update himself
    login_user_via_session(client, email=user['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=user['pid']),
                     data=json.dumps(user.dumps()),
                     headers=headers)
    assert res.status_code == 200

    # Logged as user and update other
    login_user_via_session(client, email=user['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=moderator['pid']),
                     data=json.dumps(moderator.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=submitter['pid']),
                     data=json.dumps(submitter.dumps()),
                     headers=headers)
    assert res.status_code == 200

    login_user_via_session(client, email=submitter['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=user['pid']),
                     data=json.dumps(user.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=moderator['pid']),
                     data=json.dumps(moderator.dumps()),
                     headers=headers)
    assert res.status_code == 200

    login_user_via_session(client, email=moderator['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=user['pid']),
                     data=json.dumps(user.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=user['pid']),
                     data=json.dumps(user.dumps()),
                     headers=headers)
    assert res.status_code == 200

    # Logged as admin, try to update super user
    login_user_via_session(client, email=admin['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=superuser['pid']),
                     data=json.dumps(superuser.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=user['pid']),
                     data=json.dumps(user.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.user_item',
                             pid_value=user['pid']),
                     data=json.dumps(user.dumps()),
                     headers=headers)
    assert res.status_code == 200


def test_delete(client, make_user, superuser, admin, moderator, submitter,
                user):
    """Test delete users permissions."""
    # Not logged
    res = client.delete(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.delete(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.delete(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.delete(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 204

    # Create a new user
    user = make_user('user', 'org3')

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.delete(
        url_for('invenio_records_rest.user_item', pid_value=user['pid']))
    assert res.status_code == 204
