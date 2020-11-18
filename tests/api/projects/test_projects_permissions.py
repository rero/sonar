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

"""Test project permissions."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session

from sonar.modules.deposits.api import DepositRecord


def test_list(app, client, make_project, superuser, admin, moderator,
              submitter, user):
    """Test list projects permissions."""
    make_project('submitter', 'org')
    make_project('admin', 'org')
    make_project('submitter', 'org2')

    # Not logged
    res = client.get(url_for('invenio_records_rest.proj_list'))
    assert res.status_code == 401

    # Not logged but permission checks disabled
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    res = client.get(url_for('invenio_records_rest.proj_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 3
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url_for('invenio_records_rest.proj_list'))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(url_for('invenio_records_rest.proj_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url_for('invenio_records_rest.proj_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 2

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('invenio_records_rest.proj_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 2

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.proj_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 3


def test_create(client, project_json, superuser, admin, moderator, submitter,
                user):
    """Test create project permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.post(url_for('invenio_records_rest.proj_list'),
                      data=json.dumps(project_json),
                      headers=headers)
    assert res.status_code == 401

    # User
    login_user_via_session(client, email=user['email'])
    res = client.post(url_for('invenio_records_rest.proj_list'),
                      data=json.dumps(project_json),
                      headers=headers)
    assert res.status_code == 403

    # submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.post(url_for('invenio_records_rest.proj_list'),
                      data=json.dumps(project_json),
                      headers=headers)
    assert res.status_code == 201

    # Moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.post(url_for('invenio_records_rest.proj_list'),
                      data=json.dumps(project_json),
                      headers=headers)
    assert res.status_code == 201

    # Admin
    login_user_via_session(client, email=admin['email'])
    res = client.post(url_for('invenio_records_rest.proj_list'),
                      data=json.dumps(project_json),
                      headers=headers)
    assert res.status_code == 201

    # Super user
    login_user_via_session(client, email=superuser['email'])
    res = client.post(url_for('invenio_records_rest.proj_list'),
                      data=json.dumps(project_json),
                      headers=headers)
    assert res.status_code == 201


def test_read(client, make_project, make_user, superuser, admin, moderator,
              submitter, user):
    """Test read project permissions."""
    project1 = make_project('submitter', 'org')
    project2 = make_project('submitter', 'org2')

    # Not logged
    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 200

    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project2['pid']))
    assert res.status_code == 200

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 200

    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project2['pid']))
    assert res.status_code == 200

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 200

    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project2['pid']))
    assert res.status_code == 200

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 200

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 200


def test_update(client, make_project, superuser, admin, moderator, submitter,
                user):
    """Test update project permissions."""
    project1 = make_project('submitter', 'org')
    project2 = make_project('submitter', 'org2')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project1['pid']),
                     data=json.dumps(project1.dumps()),
                     headers=headers)
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project1['pid']),
                     data=json.dumps(project1.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project1['pid']),
                     data=json.dumps(project1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project2['pid']),
                     data=json.dumps(project2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project1['pid']),
                     data=json.dumps(project1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project2['pid']),
                     data=json.dumps(project2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project1['pid']),
                     data=json.dumps(project1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project2['pid']),
                     data=json.dumps(project2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project1['pid']),
                     data=json.dumps(project1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.proj_item',
                             pid_value=project2['pid']),
                     data=json.dumps(project2.dumps()),
                     headers=headers)
    assert res.status_code == 200


def test_delete(client, db, document, make_project, superuser, admin,
                moderator, submitter, user):
    """Test delete deposits permissions."""
    project1 = make_project('submitter', 'org')
    project2 = make_project('submitter', 'org2')

    # Not logged
    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project2['pid']))
    assert res.status_code == 403

    project1 = make_project('submitter', 'org')

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project2['pid']))
    assert res.status_code == 403

    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 204

    project1 = make_project('submitter', 'org')

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project2['pid']))
    assert res.status_code == 403

    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 204

    project1 = make_project('submitter', 'org')

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 204

    project1 = make_project('submitter', 'org')

    # Cannot remove project as it is linked to document.
    document['projects'] = [{
        '$ref':
        'https://sonar.ch/api/projects/{pid}'.format(pid=project1['pid'])
    }]
    document.commit()
    document.reindex()
    db.session.commit()

    res = client.delete(
        url_for('invenio_records_rest.proj_item', pid_value=project1['pid']))
    assert res.status_code == 403
