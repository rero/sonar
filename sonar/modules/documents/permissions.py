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

"""Permissions for documents."""

from flask import current_app, request
from invenio_files_rest.models import Bucket, ObjectVersion
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import FilesPermission, RecordPermission

from .utils import get_file_restriction, get_organisations


class DocumentPermission(RecordPermission):
    """Documents permissions."""

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        view = request.args.get('view')

        # Documents are accessible in public view, but eventually filtered
        # later by organisation
        if view:
            return True

        # Only for moderators users.
        if (not user or not user.is_moderator or not current_organisation):
            return False

        return True

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Only for moderators users
        return user and user.is_moderator

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Superuser is allowed.
        if user and user.is_superuser:
            return True

        document = DocumentRecord.get_record_by_pid(record['pid'])
        document = document.replace_refs()
        # Moderator can read their own documents.
        if user and user.is_moderator:
            if document.has_organisation(current_organisation['pid']):
                return True
        return not document.is_masked

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        if not user or not user.is_moderator:
            return False

        if user.is_superuser:
            return True

        document = DocumentRecord.get_record_by_pid(record['pid'])
        document = document.replace_refs()

        # Moderator can update their own documents.
        if not document.has_organisation(current_organisation['pid']):
            return False

        user = user.replace_refs()

        return document.has_subdivision(user.get('subdivision', {}).get('pid'))

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Delete is only for admins.
        if not user or not user.is_admin:
            return False

        # Check delete conditions and consider same rules as update
        return cls.can_delete(user, record) and cls.update(user, record)

    @classmethod
    def can_delete(cls, user, record):
        """Delete permission conditions.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Delete only documents with no registred URN
        try:
            document = DocumentRecord.get_record_by_pid(record['pid'])
            if document:
                urn_identifier = PersistentIdentifier\
                    .get_by_object('urn', 'rec', document.id)
                urn_config = current_app.config.get("SONAR_APP_DOCUMENT_URN")
                org_pid = document.replace_refs()\
                    .get("organisation", [{}])[0].get("pid")

                if config := urn_config.get("organisations", {}).get(org_pid):
                    if record.get("documentType") in config.get("types")\
                        and urn_identifier\
                            and urn_identifier.is_registered():
                        return False
        except PIDDoesNotExistError:
            pass

        return True

class DocumentFilesPermission(FilesPermission):
    """Documents files permissions.

    Write operations are limited to admin users, read depends if the
    corresponding document is masked or if the file is restricted.
    """

    @classmethod
    def get_document(cls, parent_record):
        """Get the parent document."""
        return DocumentRecord.get_record_by_pid(parent_record.get('pid'))

    @classmethod
    def read(cls, user, record, pid, parent_record):
        """Read permission check.

        :param user: current user record.
        :param record: Record to check.
        :param pid: The :class:`invenio_pidstore.models.PersistentIdentifier`
        instance.
        :param parent_record: the record related to the bucket.
        :returns: True is action can be done.
        """
        # Superuser is allowed.
        if user and user.is_superuser:
            return True
        document = cls.get_document(parent_record)
        if document and not DocumentPermission.read(user, document):
            return False

        # read the bucket metadata
        # TODO: filter the list of files based on embargo
        if isinstance(record, Bucket):
            return True
        file_type = document.files[record.key]['type']
        if file_type == 'fulltext' and (not user or not user.is_admin):
            return False
        file_restriction = get_file_restriction(
            document.files[record.key],
            get_organisations(document),
            True
        )
        return not file_restriction.get('restricted', True)

    @classmethod
    def update(cls, user, record, pid, parent_record):
        """Update permission check.

        :param user: Current user record.
        :param record: Record to check.
        :param pid: The :class:`invenio_pidstore.models.PersistentIdentifier`
        instance.
        :param parent_record: the record related to the bucket.
        :returns: True is action can be done.
        """
        if user and user.is_superuser:
            return True
        document = cls.get_document(parent_record)
        if document:
            return DocumentPermission.update(user, document)
        return False

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
        document = cls.get_document(parent_record)
        if isinstance(record, ObjectVersion):
            file_type = document.files[record.key]['type']
            if file_type == 'file' and record.mimetype == 'application/pdf':
                return DocumentPermission.can_delete(user, parent_record)\
                    and cls.update(user, record, pid, parent_record)
        return cls.update(user, record, pid, parent_record)
