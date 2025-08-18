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

"""Permissions for organisations."""

from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import FilesPermission, RecordPermission

from .api import OrganisationRecord


class OrganisationPermission(RecordPermission):
    """Organisations permissions."""

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Only for admin users at least.
        return bool(user and user.is_admin)

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Only superuser can create an organisation.
        return bool(user and user.is_superuser)

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Only for admin users
        if not user or not user.is_admin:
            return False

        # Super user is allowed
        if user.is_superuser:
            return True

        # For admin users, they can read only their own organisation.
        return current_organisation["pid"] == record["pid"]

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Same rules as read.
        return cls.read(user, record)

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True if action can be done.
        """
        return bool(user and user.is_superuser)


class OrganisationFilesPermission(FilesPermission):
    """Organisation files permissions.

    Follows the same rules than the corresponding organisation except for read
    which is always accessible.
    """

    @classmethod
    def get_organisation(cls, parent_record):
        """Get the organisation from the parent record."""
        return OrganisationRecord.get_record_by_pid(parent_record["pid"])

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

        Mainly the same behavior than the corresponding organisation record.

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
        organisation = cls.get_organisation(parent_record)
        return organisation and OrganisationPermission.update(user, organisation)

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
