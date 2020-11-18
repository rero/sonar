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

"""Permissions for projects."""

from flask import request

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import RecordPermission
from sonar.modules.projects.api import ProjectRecord
from sonar.modules.users.api import current_user_record


class ProjectPermission(RecordPermission):
    """Projects permissions."""

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param user: Logged user.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        return (False if not current_user_record else
                current_user_record.is_submitter)

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param user: Logged user.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        return cls.list(user, record)

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param user: Logged user.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # At least for submitters logged users.
        if not current_user_record or not current_user_record.is_submitter:
            return False

        return True

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param user: Logged user.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # At least for submitters logged users.
        if not current_user_record or not current_user_record.is_submitter:
            return False

        # Superuser is allowd
        if current_user_record.is_superuser:
            return True

        project = ProjectRecord.get_record_by_pid(record['pid'])
        project = project.replace_refs()

        # For admin or moderators users, they can update only their
        # organisation's projects.
        if current_user_record.is_moderator:
            return current_organisation['pid'] == project['organisation'][
                'pid']

        # For submitters, they can only modify their own projects
        return current_user_record['pid'] == project['user']['pid']

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param user: Logged user.
        :param record: Record to check.
        :returns: True if action can be done.
        """
        documents = DocumentRecord.get_documents_by_project(record['pid'])
        if documents:
            return False

        return cls.update(user, record)
