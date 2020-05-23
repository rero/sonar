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

"""Test organisations permissions."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(client, make_organisation, superuser, admin, moderator,
              publisher, user):
    """Test list organisations permissions."""
    make_organisation('org2')

    # Not logged
    res = client.get(url_for('invenio_records_rest.org_list'))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url_for('invenio_records_rest.org_list'))
    assert res.status_code == 403

    # Logged as publisher
    login_user_via_session(client, email=publisher['email'])
    res = client.get(url_for('invenio_records_rest.org_list'))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url_for('invenio_records_rest.org_list'))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('invenio_records_rest.org_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.org_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 2


def test_create(client, superuser, admin, moderator, publisher, user):
    """Test create organisations permissions."""
    data = {'code': 'org2', 'name': 'org2'}

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.post(url_for('invenio_records_rest.org_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 401

    # User
    login_user_via_session(client, email=user['email'])
    res = client.post(url_for('invenio_records_rest.org_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 403

    # Publisher
    login_user_via_session(client, email=publisher['email'])
    res = client.post(url_for('invenio_records_rest.org_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 403

    # Moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.post(url_for('invenio_records_rest.org_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 403

    # Admin
    login_user_via_session(client, email=admin['email'])
    res = client.post(url_for('invenio_records_rest.org_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 403

    # Super user
    login_user_via_session(client, email=superuser['email'])
    res = client.post(url_for('invenio_records_rest.org_list'),
                      data=json.dumps(data),
                      headers=headers)
    assert res.status_code == 201
    assert res.json['metadata']['pid'] == 'org2'


def test_read(client, make_organisation, superuser, admin, moderator,
              publisher, user):
    """Test read organisations permissions."""
    make_organisation('org2')

    # Not logged
    res = client.get(url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403

    # Logged as publisher
    login_user_via_session(client, email=publisher['email'])
    res = client.get(url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': False,
        'read': True,
        'update': True
    }

    # Logged as admin of other organisation
    res = client.get(url_for('invenio_records_rest.org_item',
                             pid_value='org2'))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 200

    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.org_item',
                             pid_value='org2'))
    assert res.status_code == 200
    assert res.json['metadata']['permissions'] == {
        'delete': False,
        'read': True,
        'update': True
    }


def test_update(client, make_organisation, superuser, admin, moderator,
                publisher, user):
    """Test update organisations permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    org = make_organisation('org')
    org2 = make_organisation('org2')

    # Not logged
    res = client.put(url_for('invenio_records_rest.org_item', pid_value='org'),
                     data=json.dumps(org.dumps()),
                     headers=headers)
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.put(url_for('invenio_records_rest.org_item', pid_value='org'),
                     data=json.dumps(org.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as publisher
    login_user_via_session(client, email=publisher['email'])
    res = client.put(url_for('invenio_records_rest.org_item', pid_value='org'),
                     data=json.dumps(org.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.put(url_for('invenio_records_rest.org_item', pid_value='org'),
                     data=json.dumps(org.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.put(url_for('invenio_records_rest.org_item', pid_value='org'),
                     data=json.dumps(org.dumps()),
                     headers=headers)
    assert res.status_code == 200

    # Logged as admin of other organisation
    res = client.put(url_for('invenio_records_rest.org_item',
                             pid_value=org2['pid']),
                     data=json.dumps(org2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.org_item',
                             pid_value=org['pid']),
                     data=json.dumps(org.dumps()),
                     headers=headers)
    assert res.status_code == 200

    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.org_item',
                             pid_value=org2['pid']),
                     data=json.dumps(org2.dumps()),
                     headers=headers)
    assert res.status_code == 200


def test_delete(client, superuser, admin,
                moderator, publisher, user):
    """Test delete organisations permissions."""
    # Not logged
    res = client.delete(
        url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.delete(
        url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403

    # Logged as publisher
    login_user_via_session(client, email=publisher['email'])
    res = client.delete(
        url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.delete(
        url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.delete(
        url_for('invenio_records_rest.org_item', pid_value='org'))
    assert res.status_code == 403
