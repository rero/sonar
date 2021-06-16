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

"""Record permissions."""

from sonar.modules.documents.api import DocumentSearch
from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import RecordPermission as BaseRecordPermission

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

        record = Record.get_record_by_pid(record['pid'])
        record = record.replace_refs()

        return current_organisation['pid'] == record['organisation']['pid']

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
        results = DocumentSearch().filter(
            'term', subdivisions__pid=record['pid']).source(includes=['pid'])

        # Cannot remove subdivision associated to a record
        if results.count():
            return False

        if not cls.read(user, record):
            return False

        return cls.create(user, record)
