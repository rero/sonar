# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Permissions for users."""

from sonar.modules.organisations.api import OrganisationRecord, current_organisation
from sonar.modules.permissions import RecordPermission
from sonar.modules.users.api import UserRecord


class UserPermission(RecordPermission):
    """Users permissions."""

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        return bool(user)

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        if not user:
            return False

        return user.is_admin

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        if not user:
            return False

        # Can read himself in all cases
        if user["pid"] == record["pid"]:
            return True

        # If not admin, no access
        if not user.is_admin:
            return False

        # Superuser is allowed
        if user.is_superuser:
            return True

        # Cannot read superusers records
        if record["role"] == UserRecord.ROLE_SUPERUSER:
            return False

        user = UserRecord.get_record_by_pid(record["pid"])
        user = user.replace_refs()

        if not user.get("organisation"):
            return True

        return current_organisation["pid"] == user["organisation"]["pid"]

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Same rules as read permission.
        return cls.read(user, record)

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # At least for admin logged users.
        if not user or not user.is_admin:
            return False

        # Superuser is allowed
        if user.is_superuser:
            return True

        # Cannot delete himself
        if user["pid"] == record["pid"]:
            return False

        if not record.get("organisation"):
            return False

        # For admin read is only for logged user organisation
        if record["organisation"].get("$ref"):
            return current_organisation["pid"] == OrganisationRecord.get_pid_by_ref_link(record["organisation"]["$ref"])

        return current_organisation["pid"] == record["organisation"]["pid"]
