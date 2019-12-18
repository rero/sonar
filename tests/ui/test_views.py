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

"""Test SONAR views."""

import pytest
from flask import url_for
from invenio_accounts.testutils import login_user_via_session

from sonar.modules.users.api import UserRecord


def test_error(client):
    """Test error page"""
    with pytest.raises(Exception):
        assert client.get(url_for('sonar.error'))


def test_admin_record_page(app, admin_user_fixture):
    """Test admin page redirection to defaults."""
    with app.test_client() as client:
        file_url = url_for('sonar.manage')

        res = client.get(file_url)
        assert res.status_code == 401

        login_user_via_session(client, email=admin_user_fixture.email)

        file_url = url_for('sonar.manage')

        res = client.get(file_url)
        assert res.status_code == 302
        assert '/records/documents' in res.location

        file_url = url_for('sonar.manage', path='records/documents')
        res = client.get(file_url)
        assert res.status_code == 200
        assert '<admin-root>' in str(res.data)


def test_logged_user(app, client, monkeypatch):
    """Test logged user page."""
    url = url_for('sonar.logged_user')

    monkeypatch.setattr(
        'sonar.modules.users.api.UserRecord.get_user_by_current_user', lambda *
        args: None)

    res = client.get(url)
    assert b'{}' in res.data

    user = UserRecord.create({
        'pid': '1',
        'email': 'admin@test.com',
        'full_name': 'Jules Brochu',
        'roles': ['user'],
        'institution': {
            '$ref': 'https://sonar.ch/api/institutions/usi'
        }
    })

    # Mock get current user because data are not indexed to ES.
    monkeypatch.setattr(
        'sonar.modules.users.api.UserRecord.get_user_by_current_user', lambda *
        args: user)

    user = UserRecord.create({
        'pid': '1',
        'email': 'admin@test.com',
        'full_name': 'Jules Brochu',
        'roles': ['user'],
        'institution': {
            'pid': 'usi',
            'name': 'Università della Svizzera italiana'
        }
    })

    # Mock replace references because data are not indexed to ES.
    monkeypatch.setattr(
        'sonar.modules.users.api.UserRecord.replace_refs', lambda *
        args: user)

    res = client.get(url)
    assert b'"email":"admin@test.com"' in res.data

    res = client.get(url + '?resolve=1')
    assert b'"email":"admin@test.com"' in res.data
    assert b'"pid":"usi"' in res.data
