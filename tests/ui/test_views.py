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
from flask_principal import ActionNeed
from invenio_access.models import ActionUsers, Role


def test_error(client):
    """Test error page"""
    with pytest.raises(Exception):
        assert client.get(url_for('sonar.error'))


def test_admin_record_page(app, db, user_fixture):
    """Test admin page redirection to defaults."""
    datastore = app.extensions['security'].datastore
    user = datastore.find_user(email='john.doe@test.com')

    admin = Role(name='admin')
    admin.users.append(user)

    db.session.add(admin)
    db.session.commit()

    with app.test_client() as client:
        if user:
            file_url = url_for('sonar.manage')

            res = client.get(file_url)
            assert res.status_code == 401

            # Login as user
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['_fresh'] = True

            res = client.get(file_url)
            assert res.status_code == 403

            db.session.add(
                ActionUsers.allow(ActionNeed('admin-access'), user=user))
            db.session.commit()

            file_url = url_for('sonar.manage')

            res = client.get(file_url)
            assert res.status_code == 302
            assert '/records/documents' in res.location

            file_url = url_for('sonar.manage', path='records/documents')
            res = client.get(file_url)
            assert res.status_code == 200
            assert '<admin-root>' in str(res.data)
