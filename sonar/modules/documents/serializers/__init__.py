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

"""Document serializers."""

from __future__ import absolute_import, print_function

from datetime import datetime

from flask import current_app, request
from invenio_records_rest.serializers.response import record_responsify, \
    search_responsify

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.documents.serializers.dc import SonarDublinCoreSerializer
from sonar.modules.documents.serializers.google_scholar import \
    SonarGoogleScholarSerializer
from sonar.modules.documents.serializers.schemaorg import \
    SonarSchemaOrgSerializer
from sonar.modules.documents.serializers.schemas.dc import DublinCoreV1
from sonar.modules.documents.serializers.schemas.google_scholar import \
    GoogleScholarV1
from sonar.modules.documents.serializers.schemas.schemaorg import SchemaOrgV1
from sonar.modules.organisations.api import OrganisationRecord, \
    current_organisation
from sonar.modules.serializers import JSONSerializer as _JSONSerializer
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.users.api import current_user_record
from sonar.modules.utils import get_language_value

from ..marshmallow import DocumentSchemaV1


class JSONSerializer(_JSONSerializer):
    """JSON serializer for documents."""

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        view = request.args.get('view')

        if view:
            if view != current_app.config.get(
                    'SONAR_APP_DEFAULT_ORGANISATION'):
                results['aggregations'].pop('organisation', {})
        else:
            if current_user_record and not current_user_record.is_superuser:
                results['aggregations'].pop('organisation', {})

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
            organisation = OrganisationRecord.get_record_by_pid(
                org_term['key'])
            if organisation:
                org_term['name'] = organisation['name']

        # Process facets for custom fields
        if view and view != current_app.config.get(
                'SONAR_APP_DEFAULT_ORGANISATION'):
            organisation = OrganisationRecord.get_record_by_pid(view)
        else:
            organisation = current_organisation

        for i in range(1, 4):
            if results.get('aggregations').get(f'customField{i}'):
                # The facet is displayed only in dedicated view.
                if view == current_app.config.get(
                        'SONAR_APP_DEFAULT_ORGANISATION'
                ) or not organisation or not organisation.get(
                        f'documentsCustomField{i}', {}).get('includeInFacets'):
                    results['aggregations'].pop(f'customField{i}', None)
                else:
                    if organisation[f'documentsCustomField{i}'].get('label'):
                        results['aggregations'][f'customField{i}'][
                            'name'] = get_language_value(
                                organisation[f'documentsCustomField{i}']
                                ['label'])

        # Dont display collection aggregation in the collection context
        if request.args.get('collection_view'):
            results['aggregations'].pop('collection', None)

        # Add collection name
        for org_term in results.get('aggregations',
                                    {}).get('collection',
                                            {}).get('buckets', []):
            collection = CollectionRecord.get_record_by_pid(org_term['key'])
            if collection:
                org_term['name'] = get_language_value(collection['name'])

        # Don't display subdivision in global context
        if view and view == current_app.config.get(
                'SONAR_APP_DEFAULT_ORGANISATION'):
            results['aggregations'].pop('subdivision', {})

        return super(JSONSerializer,
                     self).post_process_serialize_search(results, pid_fetcher)


# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(DocumentSchemaV1)
#: Dublin Core serializer
dc_v1 = SonarDublinCoreSerializer(DublinCoreV1, replace_refs=True)
#: schema.org serializer
schemaorg_v1 = SonarSchemaOrgSerializer(SchemaOrgV1, replace_refs=True)
#: google scholar serializer
google_scholar_v1 = SonarGoogleScholarSerializer(GoogleScholarV1,
                                                 replace_refs=True)

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

# OAI-PMH record serializers.
# ===========================
#: OAI-PMH OAI Dublin Core record serializer.
oaipmh_oai_dc = dc_v1.serialize_oaipmh
