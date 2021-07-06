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

"""Test SONAR views."""

from datetime import datetime

import pytest
import pytz
from flask import url_for
from invenio_accounts.testutils import login_user_via_session, \
    login_user_via_view

from sonar.theme.views import format_date, record_image_url


def test_error(client):
    """Test error page"""
    with pytest.raises(Exception):
        assert client.get(url_for('sonar.error'))


def test_admin_record_page(app, admin, user_without_role):
    """Test admin page redirection to defaults."""
    with app.test_client() as client:
        file_url = url_for('sonar.manage')

        # User is not logged
        res = client.get(file_url)
        assert res.status_code == 401

        # User is logged, but is not allowed to access the page.
        login_user_via_session(client, email=user_without_role.email)
        res = client.get(file_url)
        assert res.status_code == 403

        # OK, but redirected to the default page
        login_user_via_session(client, email=admin['email'])
        res = client.get(file_url)
        assert res.status_code == 200

        # OK
        file_url = url_for('sonar.manage', path='records/documents')
        res = client.get(file_url)
        assert res.status_code == 200
        assert '<sonar-root>' in str(res.data)


def test_logged_user(app, client, superuser, admin, moderator, submitter,
                     user):
    """Test logged user page."""
    url = url_for('sonar.logged_user')

    res = client.get(url)
    assert b'{}' in res.data

    # Logged as admin
    login_user_via_session(client, email=admin['email'])
    res = client.get(url)
    assert b'"email":"orgadmin@rero.ch"' in res.data
    assert res.json['metadata']['permissions']['documents']['add']
    assert not res.json['metadata']['permissions']['organisations']['add']
    assert res.json['metadata']['permissions']['users']['add']
    assert res.json['metadata']['permissions']['deposits']['add']

    res = client.get(url + '?resolve=1')
    assert b'"email":"orgadmin@rero.ch"' in res.data
    assert b'"pid":"org"' in res.data

    # Logged as superuser
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url)
    assert b'"email":"orgsuperuser@rero.ch"' in res.data
    assert res.json['metadata']['permissions']['documents']['add']
    assert res.json['metadata']['permissions']['organisations']['add']
    assert res.json['metadata']['permissions']['users']['add']
    assert res.json['metadata']['permissions']['deposits']['add']
    assert res.json['metadata']['permissions']['documents']['list']
    assert res.json['metadata']['permissions']['organisations']['list']
    assert res.json['metadata']['permissions']['users']['list']
    assert res.json['metadata']['permissions']['deposits']['list']

    # Logged as moderator
    login_user_via_session(client, email=moderator['email'])
    res = client.get(url)
    assert b'"email":"orgmoderator@rero.ch"' in res.data
    assert res.json['metadata']['permissions']['documents']['add']
    assert not res.json['metadata']['permissions']['organisations']['add']
    assert not res.json['metadata']['permissions']['users']['add']
    assert res.json['metadata']['permissions']['deposits']['add']
    assert res.json['metadata']['permissions']['documents']['list']
    assert not res.json['metadata']['permissions']['organisations']['list']
    assert res.json['metadata']['permissions']['users']['list']
    assert res.json['metadata']['permissions']['deposits']['list']

    # Logged as submitter
    login_user_via_session(client, email=submitter['email'])
    res = client.get(url)
    assert b'"email":"orgsubmitter@rero.ch"' in res.data
    assert not res.json['metadata']['permissions']['documents']['add']
    assert not res.json['metadata']['permissions']['organisations']['add']
    assert not res.json['metadata']['permissions']['users']['add']
    assert res.json['metadata']['permissions']['deposits']['add']
    assert not res.json['metadata']['permissions']['documents']['list']
    assert not res.json['metadata']['permissions']['organisations']['list']
    assert res.json['metadata']['permissions']['users']['list']
    assert res.json['metadata']['permissions']['deposits']['list']

    # Logged as user
    login_user_via_session(client, email=user['email'])
    res = client.get(url)
    assert b'"email":"orguser@rero.ch"' in res.data
    assert not res.json['metadata']['permissions']['documents']['add']
    assert not res.json['metadata']['permissions']['organisations']['add']
    assert not res.json['metadata']['permissions']['users']['add']
    assert not res.json['metadata']['permissions']['deposits']['add']
    assert not res.json['metadata']['permissions']['documents']['list']
    assert not res.json['metadata']['permissions']['organisations']['list']
    assert res.json['metadata']['permissions']['users']['list']
    assert not res.json['metadata']['permissions']['deposits']['list']


def test_schemas(client, admin, user):
    """Test JSON schemas endpoint."""
    res = client.get(url_for('sonar.schemas', record_type='documents'))
    assert res.status_code == 200
    assert res.json['schema']['properties'].get('organisation')

    res = client.get(url_for('sonar.schemas', record_type='users'))
    assert res.status_code == 200
    assert res.json['schema']['properties'].get('organisation')
    assert res.json['schema']['properties'].get('role')

    login_user_via_session(client, email=admin['email'])

    res = client.get(url_for('sonar.schemas', record_type='documents'))
    assert res.status_code == 200
    assert not res.json['schema']['properties'].get('organisation')

    res = client.get(url_for('sonar.schemas', record_type='users'))
    assert res.status_code == 200
    assert not res.json['schema']['properties'].get('organisation')
    assert res.json['schema']['properties'].get('role')
    assert len(res.json['schema']['properties']['role']['enum']) == 4

    res = client.get(url_for('sonar.schemas', record_type='not_existing'))
    assert res.status_code == 404

    # Organisations, with admin user --> no fields `isShared` and `isDedicated`
    res = client.get(url_for('sonar.schemas', record_type='organisations'))
    assert res.status_code == 200
    assert 'isShared' not in res.json['schema']['propertiesOrder']
    assert 'isDedicated' not in res.json['schema']['propertiesOrder']

    login_user_via_session(client, email=user['email'])

    res = client.get(url_for('sonar.schemas', record_type='users'))
    assert res.status_code == 200
    assert not res.json['schema']['properties'].get('organisation')
    assert not res.json['schema']['properties'].get('role')

    # Projects
    res = client.get(url_for('sonar.schemas', record_type='projects'))
    assert res.status_code == 200
    assert not res.json['schema']['properties']['metadata']['properties'].get(
        'organisation')
    assert not res.json['schema']['properties'].get('role')
    assert 'organisation' not in res.json['schema']['properties']['metadata'][
        'propertiesOrder']


def test_profile(client, user):
    """Test profile page."""
    # Not logged
    res = client.get(url_for('sonar.profile'))
    assert res.status_code == 302
    assert res.location.find('/login/') != -1

    # Logged and redirected with user PID as param
    login_user_via_view(client, email=user['email'], password='123456')
    res = client.get(url_for('sonar.profile'))
    assert res.status_code == 302
    assert res.location.find(
        '/users/profile/{pid}'.format(pid=user['pid'])) != -1

    # Logged
    res = client.get(url_for('sonar.profile', pid=user['pid']))
    assert res.status_code == 200

    # Wrong PID
    res = client.get(url_for('sonar.profile', pid='wrong'))
    assert res.status_code == 403


def test_record_image_url():
    """Test getting record image url."""
    # No file key
    assert not record_image_url({})

    # No files
    assert not record_image_url({'_files': []})

    # No images
    assert not record_image_url(
        {'_files': [{
            'bucket': '1234',
            'key': 'test.pdf'
        }]})

    record = {
        '_files': [{
            'bucket': '1234',
            'key': 'test.jpg'
        }, {
            'bucket': '1234',
            'key': 'test2.jpg'
        }]
    }

    # Take the first file
    assert record_image_url(record) == '/api/files/1234/test.jpg'

    # Take files corresponding to key
    assert record_image_url(record, 'test2.jpg') == '/api/files/1234/test2.jpg'


def test_rerodoc_redirection(client, document):
    """Test redirection with RERODOC identifier."""
    res = client.get(url_for('sonar.rerodoc_redirection', pid='NOT-EXISTING'))
    assert res.status_code == 404

    res = client.get(url_for('sonar.rerodoc_redirection', pid='111111'))
    assert res.status_code == 302
    assert res.location.find(
        '/global/documents/{pid}'.format(pid=document['pid'])) != -1


def test_format_date(app):
    """Test date formatting."""
    assert format_date('1984-05-01 14:30:00',
                       '%d/%m/%Y %H:%M') == '01/05/1984 16:30'

    date = datetime(1984, 5, 10, 14, 30)
    assert format_date(date, '%d/%m/%Y %H:%M') == '10/05/1984 16:30'

    timezone = pytz.timezone('Europe/Zurich')
    date = datetime(1984, 5, 10, 14, 30, tzinfo=timezone)
    assert format_date(date, '%d/%m/%Y %H:%M') == '10/05/1984 14:30'
