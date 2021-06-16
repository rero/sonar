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

"""Deposit serializers."""

from __future__ import absolute_import, print_function

from invenio_records_rest.serializers.response import record_responsify, \
    search_responsify

from sonar.modules.serializers import JSONSerializer as _JSONSerializer
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.users.api import UserRecord

from ..marshmallow import DepositSchemaV1


class JSONSerializer(_JSONSerializer):
    """JSON serializer for projects."""

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        # Add user name
        for org_term in results.get('aggregations',
                                    {}).get('user', {}).get('buckets', []):
            user = UserRecord.get_record_by_pid(org_term['key'])
            if user:
                org_term['name'] = '{last_name}, {first_name}'.format(
                    last_name=user['last_name'], first_name=user['first_name'])

        # Add subdivision name
        for org_term in results.get('aggregations',
                                    {}).get('subdivision',
                                            {}).get('buckets', []):
            subdivision = SubdivisionRecord.get_record_by_pid(org_term['key'])
            if subdivision:
                org_term['name'] = subdivision['name'][0]['value']

        return super(JSONSerializer,
                     self).post_process_serialize_search(results, pid_fetcher)


# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(DepositSchemaV1)

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
