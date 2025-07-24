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
from sonar.modules.permissions import FilesPermission as BaseFilesPermission
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
        return user and (user.is_admin or user.is_submitter)

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        return bool(user and user.is_admin)

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True is action can be done
        :rtype: bool
        """
        if user and user.is_superuser:
            return True

        if not (user and user.is_submitter):
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
        # not admin
        if not (user and user.is_admin):
            return False
        return cls.read(user, record)

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param UserRecord user: Current user record
        :param Record record: Record to check
        :return: True if action can be done
        :rtype: bool
        """
        # not admin
        if not (user and user.is_admin):
            return False

        results = (
            DocumentSearch()
            .filter("term", collections__pid=record["pid"])
            .source(includes=["pid"])
        )

        # Cannot remove collection associated to a record
        if results.count():
            return False

        return cls.read(user, record)


class FilesPermission(BaseFilesPermission):
    """Collection files permissions.

    Follows the same rules than the corresponding collection except for read
    which is always accessible.
    """

    @classmethod
    def get_collection(cls, parent_record):
        """Get the collection record from the parent record."""
        return Record.get_record_by_pid(parent_record["pid"])

    @classmethod
    def read(cls, user, record, pid, parent_record):
        """Read permission check.

        :param user: Current user record.
        :param record: Record to check.
        :param pid: The :class:`invenio_pidstore.models.PersistentIdentifier`
        instance.
        :param parent_record: the record related to the bucket.
        :returns: True is action can be done.
        """
        # allowed for anyone
        return True

    @classmethod
    def update(cls, user, record, pid, parent_record):
        """Update permission check.

        Mainly the same behavior than the corresponding collection record.

        :param user: Current user record.
        :param record: Record to check.
        :param pid: The :class:`invenio_pidstore.models.PersistentIdentifier`
        instance.
        :param parent_record: the record related to the bucket.
        :returns: True is action can be done.
        """
        # Superuser is allowed.
        if user and user.is_superuser:
            return True
        collection = cls.get_collection(parent_record)
        return collection and RecordPermission.update(user, collection)

    @classmethod
    def delete(cls, user, record, pid, parent_record):
        """Delete permission check.

        :param user: Current user record.
        :param record: Record to check.
        :param pid: The :class:`invenio_pidstore.models.PersistentIdentifier`
        instance.
        :param parent_record: the record related to the bucket.
        :returns: True is action can be done.
        """
        return cls.update(user, record, pid, parent_record)
