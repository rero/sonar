# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Record permissions."""

from sonar.modules.deposits.api import DepositSearch
from sonar.modules.documents.api import DocumentSearch
from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import RecordPermission as BaseRecordPermission
from sonar.modules.users.api import UserSearch

from .api import Record


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
        return user and user.is_submitter

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        return user and user.is_admin

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        # Only for moderator users.
        if not user or not user.is_submitter:
            return False

        # Superuser is allowed.
        if user.is_superuser:
            return True

        # No organisation.
        if not current_organisation:
            return False

        record = Record.get_record_by_pid(record["pid"])
        record = record.replace_refs()

        return current_organisation["pid"] == record["organisation"]["pid"]

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        if not cls.read(user, record):
            return False

        return cls.create(user, record)

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True if action can be done
        :rtype: bool
        """
        results = DocumentSearch().filter("term", subdivisions__pid=record["pid"]).source(includes=["pid"])

        # Cannot remove subdivision associated to a record
        if results.count():
            return False

        # Cannot remove subdivision associated to a user
        results = UserSearch().filter("term", subdivision__pid=record["pid"]).source(includes=["pid"])
        if results.count():
            return False

        # Cannot remove subdivision associated to a deposit
        results = DepositSearch().filter("term", diffusion__subdivisions__pid=record["pid"]).source(includes=["pid"])
        if results.count():
            return False

        return cls.create(user, record) if cls.read(user, record) else False
