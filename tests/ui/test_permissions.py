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

from flask_security import url_for_security
from invenio_accounts.testutils import login_user_via_view

from sonar.modules.permissions import admin_permission_factory, \
    files_permission_factory, has_admin_access, has_publisher_access, \
    has_superuser_access, record_permission_factory, wiki_edit_permission


def test_has_publisher_access(app, client, user_without_role, publisher):
    """Test if user has an publisher access."""

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert has_publisher_access()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=user_without_role.email,
                        password='123456')

    assert not has_publisher_access()

    client.get(url_for_security('logout'))

    login_user_via_view(client, email=publisher['email'], password='123456')

    assert has_publisher_access()


def test_has_admin_access(app, client, user_without_role, admin):
    """Test if user has an admin access."""

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert has_admin_access()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=user_without_role.email,
                        password='123456')

    assert not has_admin_access()

    client.get(url_for_security('logout'))

    login_user_via_view(client, email=admin['email'], password='123456')

    assert has_admin_access()


def test_has_superuser_access(app, client, user_without_role, superuser):
    """Test if user has a super admin access."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert has_superuser_access()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client,
                        email=user_without_role.email,
                        password='123456')

    assert not has_superuser_access()

    client.get(url_for_security('logout'))

    login_user_via_view(client, email=superuser['email'], password='123456')

    assert has_superuser_access()


def test_list_permission_factory(app, client, superuser):
    """Test list permission factory."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert record_permission_factory(action='list').can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    assert not record_permission_factory(action='list').can()

    login_user_via_view(client, email=superuser['email'], password='123456')
    assert record_permission_factory(action='list').can()


def test_create_permission_factory(app, client, superuser, document):
    """Test create permission factory"""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert record_permission_factory(action='create', record=document).can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    assert not record_permission_factory(action='create',
                                         record=document).can()

    login_user_via_view(client, email=superuser['email'], password='123456')
    assert record_permission_factory(action='create', record=document).can()


def test_read_permission_factory(app, client, superuser, document):
    """Test read permission factory"""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert record_permission_factory(action='read', record=document).can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    assert not record_permission_factory(action='read', record=document).can()

    login_user_via_view(client, email=superuser['email'], password='123456')
    assert record_permission_factory(action='read', record=document).can()


def test_update_permission_factory(app, client, superuser, document):
    """Test update permission factory"""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert record_permission_factory(action='update', record=document).can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    assert not record_permission_factory(action='update',
                                         record=document).can()

    login_user_via_view(client, email=superuser['email'], password='123456')
    assert record_permission_factory(action='update', record=document).can()


def test_delete_permission_factory(app, client, superuser, document):
    """Test delete permission factory"""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert record_permission_factory(action='delete', record=document).can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    assert not record_permission_factory(action='delete',
                                         record=document).can()

    login_user_via_view(client, email=superuser['email'], password='123456')
    assert record_permission_factory(action='delete', record=document).can()


def test_unknown_permission_factory(app, client, superuser, document):
    """Test unknown permission factory"""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert record_permission_factory(document, 'unknown').can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    assert not record_permission_factory(document, 'unknown').can()

    login_user_via_view(client, email=superuser['email'], password='123456')
    assert not record_permission_factory(document, 'unknown').can()


def test_files_permission_factory(app, client, admin):
    """Test files permission factory."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert files_permission_factory().can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client, email=admin['email'], password='123456')
    assert files_permission_factory().can()


def test_admin_permission_factory(app, client, superuser):
    """Test factory for admin access permission."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    assert admin_permission_factory(None).can()

    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=False)
    login_user_via_view(client, email=superuser['email'], password='123456')
    assert admin_permission_factory(None).can()


def test_wiki_edit_ui_permission(client, user, admin):
    """Test wiki edit ui permission."""
    # No access
    login_user_via_view(client, email=user['email'], password='123456')
    assert not wiki_edit_permission()

    # Logout user
    client.get(url_for_security('logout'))

    # OK user has access
    login_user_via_view(client, email=admin['email'], password='123456')
    assert wiki_edit_permission()
