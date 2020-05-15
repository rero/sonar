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

"""Project permissions management."""

from functools import wraps

from flask import abort, current_app
from flask_login import current_user
from flask_principal import ActionNeed, RoleNeed
from invenio_access import Permission
from invenio_records_rest.utils import check_elasticsearch

superuser_access_permission = Permission(ActionNeed('superuser-access'))
admin_access_permission = Permission(ActionNeed('admin-access'))
publisher_access_permission = Permission(RoleNeed('publisher'),
                                         RoleNeed('moderator'),
                                         RoleNeed('admin'),
                                         RoleNeed('superadmin'))

# Allow access without permission check
allow_access = type('Allow', (), {'can': lambda self: True})()


def has_publisher_access():
    """Check if current user has at least role publisher.

    This function is used in app context and can be called in all templates.
    """
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return True

    return publisher_access_permission.can()


def has_admin_access():
    """Check if current user has access to admin panel.

    This function is used in app context and can be called in all templates.
    """
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return True

    return admin_access_permission.can()


def has_super_admin_access():
    """Check if current user has access to super admin panel.

    This function is used in app context and can be called in all templates.
    """
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return True

    return superuser_access_permission.can()


def can_list_record_factory(**kwargs):
    """Factory to check if a ressource can be listed."""
    return allow_access


def can_read_record_factory(record):
    """Factory to check if a record can be read."""
    return check_elasticsearch(record)


def can_create_record_factory(**kwargs):
    """Factory to check if a record can be created."""
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return allow_access

    return admin_access_permission


def can_update_record_factory(**kwargs):
    """Factory to check if a record can be updated."""
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return allow_access

    return admin_access_permission


def can_delete_record_factory(**kwargs):
    """Factory to check if a record can be deleted."""
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return allow_access

    return admin_access_permission


def can_manage_deposit_factory(**kwargs):
    """Factory to check if a record can be deleted."""
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return allow_access

    return publisher_access_permission


def can_access_manage_view(func):
    """Check if user has access to admin views."""

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        else:
            if has_admin_access():
                return func(*args, **kwargs)

            abort(403)

    return decorated_view


def admin_permission_factory(admin_view):
    """Admin permission factory."""
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return allow_access

    return superuser_access_permission


def files_permission_factory(*kwargs):
    """Files rest permission factory."""
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return allow_access

    # TODO: Add checks for accessing files and buckets
    return allow_access


def wiki_edit_permission():
    """Wiki edition permission.

    :return: true if the logged user has the admin role.
    """
    return has_admin_access()
