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

from sonar.modules.deposits.rest import FilesResource


def test_get(app, deposit_fixture):
    """Test get a deposit by its ID."""
    response = FilesResource.get(deposit_fixture['pid'])
    assert response.status_code == 200
    assert len(response.json) == 2


def test_publish(client, db, db_user_fixture, db_moderator_fixture,
                 deposit_fixture):
    """Test publishing a deposit."""
    url = 'https://localhost:5000/deposits/{pid}/publish'.format(
        pid=deposit_fixture['pid'])

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
    deposit_fixture['status'] = 'in progress'
    deposit_fixture.commit()
    db_user_fixture['roles'] = ['moderator']
    db_user_fixture.commit()
    db.session.commit()

    response = client.post(url, data={})
    assert response.status_code == 200


def test_review(client, db, db_user_fixture, db_moderator_fixture,
                deposit_fixture):
    """Test reviewing a deposit."""
    url = 'https://localhost:5000/deposits/{pid}/review'.format(
        pid=deposit_fixture['pid'])

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Deposit is not in status to validate
    response = client.post(url)
    assert response.status_code == 400

    # No payload posted
    deposit_fixture['status'] = 'to validate'
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
                               'user': db_user_fixture['pid']
                           }),
                           headers=headers)
    assert response.status_code == 403

    # Valid approval request
    response = client.post(url,
                           data=json.dumps({
                               'action': 'approve',
                               'comment': None,
                               'user': db_moderator_fixture['pid']
                           }),
                           headers=headers)
    assert response.status_code == 200

    # Valid refusal request
    deposit_fixture['status'] = 'to validate'
    deposit_fixture.commit()
    db.session.commit()
    response = client.post(url,
                           data=json.dumps({
                               'action': 'reject',
                               'comment': 'Sorry deposit is not valid',
                               'user': db_moderator_fixture['pid']
                           }),
                           headers=headers)
    assert response.status_code == 200

    # Valid ask for changes request
    deposit_fixture['status'] = 'to validate'
    deposit_fixture.commit()
    db.session.commit()
    response = client.post(url,
                           data=json.dumps({
                               'action': 'ask-for-changes',
                               'comment': None,
                               'user': db_moderator_fixture['pid']
                           }),
                           headers=headers)
    assert response.status_code == 200
