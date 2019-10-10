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

"""Test SONAR permissions."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_view

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.permissions import can_create_record_factory, \
    can_delete_record_factory, can_list_record_factory, \
    can_read_record_factory, can_update_record_factory, \
    files_permission_factory


def test_has_admin_access(app, db, client, admin_user_fixture):
    """Test if user has an admin access."""
    user = admin_user_fixture

    login_user_via_view(client, email=user.email, password='123456')

    res = client.get(url_for('sonar.manage', path='records/documents'))
    assert res.status_code == 200


def test_has_super_admin_access(app, db, client, superadmin_user_fixture):
    """Test if user has a super admin access."""
    login_user_via_view(client,
                        email=superadmin_user_fixture.email,
                        password='123456')

    res = client.get(url_for('admin.index'))
    assert res.status_code == 200


def test_can_list_record_factory(app, client, admin_user_fixture):
    """Test is user can list record."""
    login_user_via_view(client,
                        email=admin_user_fixture.email,
                        password='123456')

    assert can_list_record_factory()
    assert can_create_record_factory()
    assert can_update_record_factory()
    assert can_delete_record_factory()

    record = DocumentRecord.create(
        {
            "pid": "2",
            "title": "The title of the record"
        }, dbcommit=True)

    assert can_read_record_factory(record)


def test_files_permission_factory(client, admin_user_fixture):
    """Test files permission factory."""
    login_user_via_view(client,
                        email=admin_user_fixture.email,
                        password='123456')
    assert files_permission_factory().can()
