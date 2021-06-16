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

"""Configuration."""

from sonar.modules.permissions import record_permission_factory

# Resource name
RESOURCE_NAME = 'subdivisions'

# JSON schema name
JSON_SCHEMA_NAME = RESOURCE_NAME[:-1]

# Module path
MODULE_PATH = f'sonar.modules.{RESOURCE_NAME}'

# PID type
PID_TYPE = 'subd'


class Configuration:
    """Resource configuration."""

    index = f'{RESOURCE_NAME}'
    schema = f'{RESOURCE_NAME}/{JSON_SCHEMA_NAME}-v1.0.0.json'
    pid_type = PID_TYPE
    resolver_url = f'/api/{RESOURCE_NAME}/<pid>'
    rest_endpoint = {
        'pid_type':
        PID_TYPE,
        'pid_minter':
        f'{RESOURCE_NAME}_id',
        'pid_fetcher':
        f'{RESOURCE_NAME}_id',
        'default_endpoint_prefix':
        True,
        'record_class':
        f'{MODULE_PATH}.api:Record',
        'search_class':
        f'{MODULE_PATH}.api:RecordSearch',
        'indexer_class':
        f'{MODULE_PATH}.api:RecordIndexer',
        'search_index':
        RESOURCE_NAME,
        'search_type':
        None,
        'record_serializers': {
            'application/json': (f'{MODULE_PATH}.serializers'
                                 ':json_v1_response'),
        },
        'search_serializers': {
            'application/json': (f'{MODULE_PATH}.serializers'
                                 ':json_v1_search'),
        },
        'record_loaders': {
            'application/json': (f'{MODULE_PATH}.loaders'
                                 ':json_v1'),
        },
        'list_route':
        f'/{RESOURCE_NAME}/',
        'item_route':
        f'/{RESOURCE_NAME}/<pid({PID_TYPE}, record_class="{MODULE_PATH}.api:Record"):pid_value>',
        'default_media_type':
        'application/json',
        'max_result_window':
        10000,
        'search_factory_imp':
        f'{MODULE_PATH}.query:search_factory',
        'create_permission_factory_imp':
        lambda record: record_permission_factory(
            action='create', cls=f'{MODULE_PATH}.permissions:RecordPermission'
        ),
        'read_permission_factory_imp':
        lambda record: record_permission_factory(
            action='read',
            record=record,
            cls=f'{MODULE_PATH}.permissions:RecordPermission'),
        'update_permission_factory_imp':
        lambda record: record_permission_factory(
            action='update',
            record=record,
            cls=f'{MODULE_PATH}.permissions:RecordPermission'),
        'delete_permission_factory_imp':
        lambda record: record_permission_factory(
            action='delete',
            record=record,
            cls=f'{MODULE_PATH}.permissions:RecordPermission'),
        'list_permission_factory_imp':
        lambda record: record_permission_factory(
            action='list',
            record=record,
            cls=f'{MODULE_PATH}.permissions:RecordPermission')
    }
