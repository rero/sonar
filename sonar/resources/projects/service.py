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

"""Projects service."""

from invenio_records_resources.services.records.schema import \
    MarshmallowServiceSchema
from invenio_records_rest.utils import obj_or_import_string

from sonar.config import DEFAULT_AGGREGATION_SIZE
from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import and_term_filter
from sonar.modules.utils import has_custom_resource

from ..service import RecordService as BaseRecordService
from ..service import RecordServiceConfig as BaseRecordServiceConfig
from .api import Record, RecordComponent
from .permissions import RecordPermissionPolicy
from .results import RecordList


class RecordServiceConfig(BaseRecordServiceConfig):
    """Projects service configuration."""

    permission_policy_cls = RecordPermissionPolicy
    record_cls = Record
    result_list_cls = RecordList
    search_sort_default = 'relevance'
    search_sort_default_no_query = 'newest'
    search_sort_options = {
        'relevance': {
            'fields': ['_score'],
        },
        'name': {
            'fields': ['metadata.name.raw']
        },
        'newest': {
            'fields': ['-metadata.startDate']
        },
        'oldest': {
            'fields': ['metadata.startDate']
        }
    }
    search_facets_options = {
        'aggs': {
            'user': {
                'terms': {
                    'field': 'metadata.user.pid',
                    'size': DEFAULT_AGGREGATION_SIZE
                }
            },
            'organisation': {
                'terms': {
                    'field': 'metadata.organisation.pid',
                    'size': DEFAULT_AGGREGATION_SIZE
                }
            },
            'status': {
                'terms': {
                    'field': 'metadata.validation.status',
                    'size': DEFAULT_AGGREGATION_SIZE
                }
            },
        },
        'filters': {
            'user': and_term_filter('metadata.user.pid'),
            'organisation': and_term_filter('metadata.organisation.pid'),
            'status': and_term_filter('metadata.validation.status'),
        }
    }
    components = BaseRecordServiceConfig.components + [RecordComponent]


class RecordService(BaseRecordService):
    """Projects service."""

    default_config = RecordServiceConfig

    @property
    def schema(self):
        """Returns the data schema instance."""
        schema_path = 'sonar.resources.projects.schema:RecordSchema'

        if has_custom_resource('projects'):
            schema_path = f'sonar.dedicated.{current_organisation["code"]}.' \
                'projects.schema:RecordSchema'

        schema = obj_or_import_string(schema_path)

        return MarshmallowServiceSchema(self, schema=schema)
