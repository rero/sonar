# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Record permissions."""

from sonar.modules.permissions import RecordPermission as BaseRecordPermission


class RecordPermission(BaseRecordPermission):
    """Record permissions."""

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        return False

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        return False

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        return user and user.is_superuser

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        return False

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True if action can be done
        :rtype: bool
        """
        return False
