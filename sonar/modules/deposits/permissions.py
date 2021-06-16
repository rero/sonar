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

"""Permissions for deposits."""

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import RecordPermission


class DepositPermission(RecordPermission):
    """Deposits permissions."""

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param user: Current user record.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        # At least for submitters logged users.
        if not user or not user.is_submitter:
            return False

        return True

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param user: Current user record.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        # No logged user.
        if not user:
            return False

        return user.is_submitter

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param user: Current user record.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        # At least for submitters logged users.
        if not user or not user.is_submitter:
            return False

        if user.is_superuser:
            return True

        deposit = DepositRecord.get_record_by_pid(record['pid'])
        deposit = deposit.replace_refs()

        # Admin is allowed only for same organisation's records
        if user.is_admin:
            return current_organisation['pid'] == deposit['user'][
                'organisation']['pid']

        # Special rules for moderators
        if user.is_moderator:
            user = user.replace_refs()

            # Deposit does not belong to user's organisation
            if current_organisation['pid'] != deposit['user']['organisation'][
                    'pid']:
                return False

            # Moderator has no subdivision, he can read the deposit
            if not user.get('subdivision'):
                return True

            # User has a subdivision, he can only read his own deposits and
            # deposits from the same subdivision
            return user['pid'] == deposit['user'][
                'pid'] or deposit.has_subdivision(
                    user.get('subdivision', {}).get('pid'))

        # Submitters have only access to their own deposits.
        return user['pid'] == deposit['user']['pid']

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param user: Current user record.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        # Same rules as read.
        return cls.read(user, record)

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param user: Current user record.
        :param recor: Record to check.
        :returns: True is action can be done.
        """
        # Cannot delete a validated deposit.
        if record['status'] == DepositRecord.STATUS_VALIDATED:
            return False

        # Same rules as read.
        return cls.read(user, record)
