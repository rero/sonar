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

from invenio_accounts.testutils import login_user_via_view

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.permissions import admin_permission_factory, \
    can_create_record_factory, can_delete_record_factory, \
    can_list_record_factory, can_read_record_factory, \
    can_update_record_factory, files_permission_factory, has_admin_access, \
    has_super_admin_access, has_user_access


def test_has_user_access(app, client, user_without_role_fixture,
                         user_fixture):
    """Test if user has an admin access."""

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert has_user_access()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=user_without_role_fixture.email,
                        password='123456')

    assert not has_user_access()

    login_user_via_view(client,
                        email=user_fixture.email,
                        password='123456')

    assert not has_user_access()


def test_has_admin_access(app, client, user_without_role_fixture,
                          admin_user_fixture):
    """Test if user has an admin access."""

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert has_admin_access()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=user_without_role_fixture.email,
                        password='123456')

    assert not has_admin_access()

    login_user_via_view(client,
                        email=admin_user_fixture.email,
                        password='123456')

    assert not has_admin_access()


def test_has_super_admin_access(app, client, user_without_role_fixture,
                                superadmin_user_fixture):
    """Test if user has a super admin access."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert has_super_admin_access()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=user_without_role_fixture.email,
                        password='123456')

    assert not has_super_admin_access()

    login_user_via_view(client,
                        email=superadmin_user_fixture.email,
                        password='123456')

    assert not has_super_admin_access()


def test_permissions_factories(app, client, admin_user_fixture):
    """Test is user can list record."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)

    assert can_list_record_factory()
    assert can_create_record_factory()
    assert can_update_record_factory()
    assert can_delete_record_factory()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)

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


def test_files_permission_factory(app, client, admin_user_fixture):
    """Test files permission factory."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert files_permission_factory().can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=admin_user_fixture.email,
                        password='123456')
    assert files_permission_factory().can()


def test_admin_permission_factory(app, client, superadmin_user_fixture):
    """Test factory for admin access permission."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert admin_permission_factory(None).can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=superadmin_user_fixture.email,
                        password='123456')
    assert admin_permission_factory(None).can()
