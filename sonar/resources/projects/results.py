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

"""Search results."""

from invenio_records_resources.services.records.results import \
    RecordList as BaseRecordList

from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.users.api import UserRecord, current_user_record


class RecordList(BaseRecordList):
    """Search list result for projects."""

    @property
    def aggregations(self):
        """Get the search result aggregations."""
        aggregations = self._results.aggregations.to_dict()

        if current_user_record:
            # Remove organisation facet for non super users
            if not current_user_record.is_superuser:
                aggregations.pop('organisation', {})

            # Remove user facet for non moderators users
            if not current_user_record.is_moderator:
                aggregations.pop('user', {})

        # Add organisation name
        for org_term in aggregations.get('organisation',
                                         {}).get('buckets', []):
            organisation = OrganisationRecord.get_record_by_pid(
                org_term['key'])
            if organisation:
                org_term['name'] = organisation['name']

        # Add user name
        for org_term in aggregations.get('user', {}).get('buckets', []):
            user = UserRecord.get_record_by_pid(org_term['key'])
            if user:
                org_term['name'] = '{last_name}, {first_name}'.format(
                    last_name=user['last_name'], first_name=user['first_name'])

        return aggregations
