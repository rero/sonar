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

"""Projects serializers."""

from __future__ import absolute_import, print_function

from invenio_records_rest.serializers.response import record_responsify, \
    search_responsify

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.serializers import JSONSerializer as _JSONSerializer
from sonar.modules.users.api import current_user_record

from ..marshmallow import ProjectSchemaV1


class JSONSerializer(_JSONSerializer):
    """JSON serializer for projects."""

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        if current_user_record:
            # Remove organisation facet for non super users
            if not current_user_record.is_superuser:
                results['aggregations'].pop('organisation', {})

            # Remove user facet for non moderators users
            if not current_user_record.is_moderator:
                results['aggregations'].pop('user', {})

        # Add organisation name
        for org_term in results.get('aggregations',
                                    {}).get('organisation',
                                            {}).get('buckets', []):
            organisation = OrganisationRecord.get_record_by_pid(
                org_term['key'])
            if organisation:
                org_term['name'] = organisation['name']

        return super(JSONSerializer,
                     self).post_process_serialize_search(results, pid_fetcher)


# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(ProjectSchemaV1)

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, 'application/json')
#: JSON record serializer for search results.
json_v1_search = search_responsify(json_v1, 'application/json')

__all__ = (
    'json_v1',
    'json_v1_response',
    'json_v1_search',
)
