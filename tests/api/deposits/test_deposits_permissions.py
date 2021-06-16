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

"""Test deposits permissions."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session

from sonar.modules.deposits.api import DepositRecord


def test_list(app, client, make_deposit, superuser, admin, moderator,
              submitter, user):
    """Test list deposits permissions."""
    make_deposit('submitter', 'org')
    make_deposit('admin', 'org')
    make_deposit('submitter', 'org2')

    # Not logged
    res = client.get(url_for('invenio_records_rest.depo_list'))
    assert res.status_code == 401

    # Not logged but permission checks disabled
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    res = client.get(url_for('invenio_records_rest.depo_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 3
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url_for('invenio_records_rest.depo_list'))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(url_for('invenio_records_rest.depo_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url_for('invenio_records_rest.depo_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 2

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url_for('invenio_records_rest.depo_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 2

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.depo_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 3


def test_create(client, deposit_json, bucket_location, superuser, admin,
                moderator, submitter, user):
    """Test create deposits permissions."""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.post(url_for('invenio_records_rest.depo_list'),
                      data=json.dumps(deposit_json),
                      headers=headers)
    assert res.status_code == 401

    # User
    login_user_via_session(client, email=user['email'])
    deposit_json['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=user['pid'])
    }
    res = client.post(url_for('invenio_records_rest.depo_list'),
                      data=json.dumps(deposit_json),
                      headers=headers)
    assert res.status_code == 403

    # submitter
    login_user_via_session(client, email=submitter['email'])
    deposit_json['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=submitter['pid'])
    }
    res = client.post(url_for('invenio_records_rest.depo_list'),
                      data=json.dumps(deposit_json),
                      headers=headers)
    assert res.status_code == 201

    # Moderator
    login_user_via_session(client, email=moderator['email'])
    deposit_json['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=moderator['pid'])
    }
    res = client.post(url_for('invenio_records_rest.depo_list'),
                      data=json.dumps(deposit_json),
                      headers=headers)
    assert res.status_code == 201

    # Admin
    login_user_via_session(client, email=admin['email'])
    deposit_json['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=admin['pid'])
    }
    res = client.post(url_for('invenio_records_rest.depo_list'),
                      data=json.dumps(deposit_json),
                      headers=headers)
    assert res.status_code == 201

    # Super user
    login_user_via_session(client, email=superuser['email'])
    deposit_json['user'] = {
        '$ref': 'https://sonar.ch/api/users/{pid}'.format(pid=superuser['pid'])
    }
    res = client.post(url_for('invenio_records_rest.depo_list'),
                      data=json.dumps(deposit_json),
                      headers=headers)
    assert res.status_code == 201


def test_read(client, db, make_deposit, make_user, superuser, admin, moderator,
              submitter, user, subdivision):
    """Test read deposits permissions."""
    deposit1 = make_deposit('submitter', 'org')
    deposit2 = make_deposit('submitter', 'org2')

    # Not logged
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 200

    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit2['pid']))
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 200

    # Moderator has subdivision, I cannot read deposit outside of his
    # subdivision
    moderator['subdivision'] = {
        '$ref': f'https://sonar.ch/api/subdivisions/{subdivision["pid"]}'
    }
    moderator.commit()
    moderator.reindex()
    db.session.commit()
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 403

    # Cannot read deposit of other organisations
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit2['pid']))
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 200

    # Cannot read deposit of other organisations
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit2['pid']))
    assert res.status_code == 403

    # Logged as admin of other organisation
    other_admin = make_user('admin', 'org2')
    login_user_via_session(client, email=other_admin['email'])
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 200


def test_update(client, make_deposit, superuser, admin, moderator, submitter,
                user):
    """Test update deposits permissions."""
    deposit1 = make_deposit('submitter', 'org')
    deposit2 = make_deposit('submitter', 'org2')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Not logged
    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit1['pid']),
                     data=json.dumps(deposit1.dumps()),
                     headers=headers)
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit1['pid']),
                     data=json.dumps(deposit1.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit1['pid']),
                     data=json.dumps(deposit1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit2['pid']),
                     data=json.dumps(deposit2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit1['pid']),
                     data=json.dumps(deposit1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit2['pid']),
                     data=json.dumps(deposit2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit1['pid']),
                     data=json.dumps(deposit1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit2['pid']),
                     data=json.dumps(deposit2.dumps()),
                     headers=headers)
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit1['pid']),
                     data=json.dumps(deposit1.dumps()),
                     headers=headers)
    assert res.status_code == 200

    login_user_via_session(client, email=superuser['email'])
    res = client.put(url_for('invenio_records_rest.depo_item',
                             pid_value=deposit2['pid']),
                     data=json.dumps(deposit2.dumps()),
                     headers=headers)
    assert res.status_code == 200


def test_delete(client, db, make_deposit, superuser, admin, moderator,
                submitter, user):
    """Test delete deposits permissions."""
    deposit1 = make_deposit('submitter', 'org')
    deposit2 = make_deposit('submitter', 'org2')

    # Not logged
    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 401

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit2['pid']))
    assert res.status_code == 403

    deposit1['status'] = DepositRecord.STATUS_VALIDATED
    deposit1.commit()
    db.session.commit()

    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 403

    deposit1['status'] = DepositRecord.STATUS_IN_PROGRESS
    deposit1.commit()
    db.session.commit()

    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 204

    deposit1 = make_deposit('submitter', 'org')

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit2['pid']))
    assert res.status_code == 403

    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 204

    deposit1 = make_deposit('submitter', 'org')

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit2['pid']))
    assert res.status_code == 403

    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 204

    deposit1 = make_deposit('submitter', 'org')

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.delete(
        url_for('invenio_records_rest.depo_item', pid_value=deposit1['pid']))
    assert res.status_code == 204
