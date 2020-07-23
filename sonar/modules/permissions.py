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

superuser_access_permission = Permission(ActionNeed('superuser-access'))
admin_access_permission = Permission(ActionNeed('admin-access'))
submitter_access_permission = Permission(RoleNeed('submitter'),
                                         RoleNeed('moderator'),
                                         RoleNeed('admin'),
                                         RoleNeed('superuser'))

# Allow access without permission check
allow_access = type('Allow', (), {'can': lambda self: True})()

# Deny access without permission check
deny_access = type('Allow', (), {'can': lambda self: False})()


def has_submitter_access():
    """Check if current user has at least role submitter.

    This function is used in app context and can be called in all templates.
    """
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return True

    return submitter_access_permission.can()


def has_admin_access():
    """Check if current user has access to admin panel.

    This function is used in app context and can be called in all templates.
    """
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return True

    return admin_access_permission.can()


def has_superuser_access():
    """Check if current user has access to super admin panel.

    This function is used in app context and can be called in all templates.
    """
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return True

    return superuser_access_permission.can()


def record_permission_factory(record=None, action=None, cls=None):
    """Record permission factory.

    :params record: Record against which to check permission.
    :params action: Action to check.
    :params cls: Class of the permission.
    :returns: Permission object.
    """
    # Permission is allowed for all actions.
    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return allow_access

    # No specific class, the base record permission class is taken.
    if not cls:
        cls = RecordPermission

    return cls.create_permission(record, action)


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

    :return: true if the logged user has the superuser role.
    """
    return has_superuser_access()


class RecordPermission:
    """Record permissions for CRUD operations."""

    list_actions = ['list']
    create_actions = ['create']
    read_actions = ['read']
    update_actions = ['update']
    delete_actions = ['delete']

    def __init__(self, record, func, user):
        """Initialize a file permission object.

        :param record: Record to check.
        :param fund: method of the class to call.
        :param user: Object representing current logged user.
        """
        self.record = record
        self.func = func
        self.user = user or current_user

    def can(self):
        """Return the permission object determining if the action can be done.

        :returns: Permission object.
        """
        return self.func(self.user, self.record)

    @classmethod
    def create_permission(cls, record, action, user=None):
        """Create a record permission.

        :param action: Action to check.
        :param user: Logged user.
        :returns: Permission object.
        """
        if action in cls.list_actions:
            return cls(record, cls.list, user)

        if action in cls.create_actions:
            return cls(record, cls.create, user)

        if action in cls.read_actions:
            return cls(record, cls.read, user)

        if action in cls.update_actions:
            return cls(record, cls.update, user)

        if action in cls.delete_actions:
            return cls(record, cls.delete, user)

        # Deny access by default
        return deny_access

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param user: Logged user.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        if user.is_anonymous:
            return False

        return has_superuser_access()

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param user: Logged user.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        if user.is_anonymous:
            return False

        return has_superuser_access()

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param user: Logged user.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        if user.is_anonymous:
            return False

        return has_superuser_access()

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param user: Logged user.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        if user.is_anonymous:
            return False

        return has_superuser_access()

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param user: Logged user.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        if user.is_anonymous:
            return False

        return has_superuser_access()
