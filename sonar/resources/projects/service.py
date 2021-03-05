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

from invenio_records_resources.services import \
    RecordServiceConfig as BaseRecordServiceConfig

from sonar.config import DEFAULT_AGGREGATION_SIZE
from sonar.modules.query import and_term_filter

from ..service import RecordService as BaseRecordService
from .api import Record, RecordComponent
from .permissions import RecordPermissionPolicy
from .results import RecordList
from .schema import RecordSchema


class RecordServiceConfig(BaseRecordServiceConfig):
    """Projects service configuration."""

    permission_policy_cls = RecordPermissionPolicy
    record_cls = Record
    result_list_cls = RecordList
    schema = RecordSchema
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
            }
        },
        'filters': {
            'user': and_term_filter('metadata.user.pid'),
            'organisation': and_term_filter('metadata.organisation.pid')
        }
    }
    components = BaseRecordServiceConfig.components + [RecordComponent]


class RecordService(BaseRecordService):
    """Projects service."""

    default_config = RecordServiceConfig
