# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Dublin Core REST serializer."""


from datetime import datetime

from flask import request

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.serializers import JSONSerializer as BasedJSONSerializer
from sonar.modules.utils import get_language_value


class JSONSerializer(BasedJSONSerializer):
    """JSON serializer for documents."""

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        view = request.args.get('view')

        if results['aggregations'].get('year'):
            results['aggregations']['year']['type'] = 'range'
            results['aggregations']['year']['config'] = {
                'min': 1950,
                'max': int(datetime.now().year),
                'step': 1
            }

        # Add organisation name
        for org_term in results.get('aggregations',
                                    {}).get('organisation',
                                            {}).get('buckets', []):
            if organisation := OrganisationRecord.get_record_by_pid(
                org_term['key']
            ):
                org_term['name'] = organisation['name']

        # Add collection name
        for org_term in results.get('aggregations',
                                    {}).get('collection',
                                            {}).get('buckets', []):
            if collection := CollectionRecord.get_record_by_pid(org_term['key']):
                org_term['name'] = get_language_value(collection['name'])
        return super(JSONSerializer,
                     self).post_process_serialize_search(results, pid_fetcher)
