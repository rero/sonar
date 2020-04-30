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

"""Test REST endpoint for deposits."""

import json

from flask import url_for

from sonar.modules.deposits.rest import FilesResource
from sonar.modules.users.api import UserRecord


def test_get(app, deposit_fixture):
    """Test get a deposit by its ID."""
    response = FilesResource.get(deposit_fixture['pid'])
    assert response.status_code == 200
    assert len(response.json) == 2


def test_post(client, deposit_fixture):
    """Test post file in deposit."""
    # Test non existing deposit
    url = '/deposits/10000/custom-files?key=1.pdf&type=additional'.format(
        pid=deposit_fixture['pid'])
    response = client.post(url)
    assert response.status_code == 400

    # Test non existing "key" paremeter
    url = '/deposits/{pid}/custom-files?type=additional'.format(
        pid=deposit_fixture['pid'])
    response = client.post(url)
    assert response.status_code == 400

    # Test non existing "type" paremeter
    url = '/deposits/{pid}/custom-files?key=1.pdf'.format(
        pid=deposit_fixture['pid'])
    response = client.post(url)
    assert response.status_code == 400

    # Test type not in "main" or "additional"
    url = '/deposits/{pid}/custom-files?key=1.pdf&type=fake'.format(
        pid=deposit_fixture['pid'])
    response = client.post(url)
    assert response.status_code == 400

    # OK
    url = '/deposits/{pid}/custom-files?key=1.pdf&type=additional'.format(
        pid=deposit_fixture['pid'])
    response = client.post(url)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json['key'] == '1.pdf'


def test_file_put(client, deposit_fixture):
    """Test putting metadata on existing file."""
    url = '/deposits/{pid}/custom-files/{key}'

    # Non existing deposit
    response = client.put(url.format(pid=10000, key='main.pdf'))
    assert response.status_code == 400

    # Non existing file
    response = client.put(
        url.format(pid=deposit_fixture['pid'], key='fake.pdf'))
    assert response.status_code == 400

    # OK
    response = client.put(url.format(pid=deposit_fixture['pid'],
                                     key='main.pdf'),
                          data=json.dumps({'label': 'Updated label'}),
                          headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert response.json['label'] == 'Updated label'

    # With embargo date
    response = client.put(url.format(pid=deposit_fixture['pid'],
                                     key='main.pdf'),
                          data=json.dumps({'embargoDate': '2021-01-01'}),
                          headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert response.json['embargoDate'] == '2021-01-01'

    # With wrong embargo date
    response = client.put(url.format(pid=deposit_fixture['pid'],
                                     key='main.pdf'),
                          data=json.dumps({'embargoDate': '2021'}),
                          headers={'Content-Type': 'application/json'})
    assert response.status_code == 400

    # Removing embargo date
    response = client.put(url.format(pid=deposit_fixture['pid'],
                                     key='main.pdf'),
                          data=json.dumps({'embargoDate': None}),
                          headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert not response.json.get('embargoDate')


def test_publish(client, db, db_user_fixture, db_moderator_fixture,
                 deposit_fixture):
    """Test publishing a deposit."""
    url = url_for('deposits.publish', pid=deposit_fixture['pid'])

    # Everything OK
    response = client.post(url, data={})
    assert response.status_code == 200

    # Deposit is not in progress
    deposit_fixture['status'] = 'validated'
    deposit_fixture.commit()
    db.session.commit()
    response = client.post(url, data={})
    assert response.status_code == 400

    # Test the publication by a moderator
    deposit_fixture['status'] = 'in_progress'
    deposit_fixture.commit()
    db_user_fixture['roles'] = ['moderator']
    db_user_fixture.commit()
    db.session.commit()

    response = client.post(url, data={})
    assert response.status_code == 200


def test_review(client, db, db_user_fixture, db_moderator_fixture,
                deposit_fixture):
    """Test reviewing a deposit."""
    url = url_for('deposits.review', pid=deposit_fixture['pid'])

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Deposit is not in status to validate
    response = client.post(url)
    assert response.status_code == 400

    # No payload posted
    deposit_fixture['status'] = 'to_validate'
    deposit_fixture.commit()
    db.session.commit()

    response = client.post(url)
    assert response.status_code == 400

    # Invalid action
    response = client.post(url,
                           data=json.dumps({
                               'action': 'unknown',
                               'comment': None
                           }),
                           headers=headers)
    assert response.status_code == 400

    # User is not a moderator
    response = client.post(url,
                           data=json.dumps({
                               'action': 'approve',
                               'comment': None,
                               'user': {
                                   '$ref':
                                   UserRecord.get_ref_link(
                                       'users', db_user_fixture['pid'])
                               }
                           }),
                           headers=headers)
    assert response.status_code == 403

    # Valid approval request
    response = client.post(url,
                           data=json.dumps({
                               'action': 'approve',
                               'comment': None,
                               'user': {
                                   '$ref':
                                   UserRecord.get_ref_link(
                                       'users', db_moderator_fixture['pid'])
                               }
                           }),
                           headers=headers)
    assert response.status_code == 200

    # Valid refusal request
    deposit_fixture['status'] = 'to_validate'
    deposit_fixture.commit()
    db.session.commit()
    response = client.post(url,
                           data=json.dumps({
                               'action': 'reject',
                               'comment': 'Sorry deposit is not valid',
                               'user': {
                                   '$ref':
                                   UserRecord.get_ref_link(
                                       'users', db_moderator_fixture['pid'])
                               }
                           }),
                           headers=headers)
    assert response.status_code == 200

    # Valid ask for changes request
    deposit_fixture['status'] = 'to_validate'
    deposit_fixture.commit()
    db.session.commit()
    response = client.post(url,
                           data=json.dumps({
                               'action': 'ask_for_changes',
                               'comment': None,
                               'user': {
                                   '$ref':
                                   UserRecord.get_ref_link(
                                       'users', db_moderator_fixture['pid'])
                               }
                           }),
                           headers=headers)
    assert response.status_code == 200


def test_extract_metadata(client, deposit_fixture):
    """Test PDF metadata extraction."""
    url = url_for('deposits.extract_metadata', pid=deposit_fixture['pid'])

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = client.get(url, headers=headers)
    assert response.status_code == 200
    assert response.json[
        'title'] == 'High-harmonic generation in quantum spin systems'

    deposit_fixture.files['main.pdf'].remove()
    response = client.get(url, headers=headers)
    assert response.status_code == 500

    response = client.get(url_for('deposits.extract_metadata',
                                  pid='not-existing'),
                          headers=headers)
    assert response.status_code == 400
