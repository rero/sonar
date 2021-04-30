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

"""Projects permission policy."""

from elasticsearch_dsl.query import Q
from flask import request
from invenio_access.permissions import any_user
from invenio_records_permissions import \
    RecordPermissionPolicy as BaseRecordPermissionPolicy
from invenio_records_permissions.generators import Admin

from sonar.modules.api import SonarRecord
from sonar.modules.documents.api import DocumentRecord
from sonar.modules.organisations.api import current_organisation
from sonar.modules.users.api import current_user_record
from sonar.modules.validation.api import Status


class Read(Admin):
    """Read projects permissions."""

    def query_filter(self, **kwargs):
        """Search filters."""
        if current_user_record.is_superuser:
            return Q('match_all')

        # For admin and moderator, only records that belongs to his
        # organisation. The same rule is applied when searching project in
        # typeahead input.
        # TODO: Find a better way for handling typeahead calls..
        if current_user_record.is_moderator or (
                request.args.get('q') and '.suggest' in request.args['q']):
            must = [
                Q('term',
                  metadata__organisation__pid=current_organisation['pid'])
            ]

            # In suggestions only records published can be queried.
            if request.args.get('q') and '.suggest' in request.args['q']:
                must.append(
                    Q('term',
                      metadata__validation__status=Status.VALIDATED)
                )

            return Q('bool', must=must)

        # For user, only records that belongs to him.
        if current_user_record.is_submitter:
            return Q('term', metadata__user__pid=current_user_record['pid'])

        return Q('match_all')


class Update(Admin):
    """Update project permissions."""

    def excludes(self, record=None, **kwargs):
        """Preventing Needs."""
        # If record is rejected, the user can't update.
        if record['metadata'].get('validation', {}).get(
                'status') == Status.REJECTED:
            return [any_user]

        # If not logged the action cannot be done.
        if not current_user_record:
            return [any_user]

        # Superuser is allowed
        if current_user_record.is_superuser:
            return []

        # For admin or moderators users, they can update only their
        # organisation's projects.
        if current_user_record.is_moderator:
            organisation_pid = SonarRecord.get_pid_by_ref_link(
                record['metadata']['organisation']
                ['$ref']) if record['metadata']['organisation'].get(
                    '$ref') else record['metadata']['organisation']['pid']
            return [
                any_user
            ] if current_organisation['pid'] != organisation_pid else []

        # For submitters, they can only modify their own projects
        if current_user_record.is_submitter:
            user_pid = SonarRecord.get_pid_by_ref_link(
                record['metadata']['user']
                ['$ref']) if record['metadata']['user'].get(
                    '$ref') else record['metadata']['user']['pid']
            return [any_user] if current_user_record['pid'] != user_pid else []

        return [any_user]


class Delete(Update):
    """Delete project permissions."""

    def excludes(self, record=None, **kwargs):
        """Preventing Needs."""
        # A project associated with documents cannot be deleted
        documents = DocumentRecord.get_documents_by_project(record['id'])
        if documents:
            return [any_user]

        return super(Delete, self).excludes(record)


class RecordPermissionPolicy(BaseRecordPermissionPolicy):
    """Projects permission policy."""

    can_search = [Read()]
    can_create = [Admin()]
    can_read = [Read()]
    can_update = [Update()]
    can_delete = [Delete()]
