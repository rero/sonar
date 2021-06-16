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

"""Marshmallow schemas."""

from functools import partial

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier
from marshmallow import fields, pre_dump, pre_load

from sonar.modules.serializers import schema_from_context
from sonar.modules.users.api import current_user_record
from sonar.modules.utils import get_language_value

from .api import Record
from .permissions import RecordPermission

schema_from_record = partial(schema_from_context, schema=Record.schema)


class RecordMetadataSchema(StrictKeysMixin):
    """Schema for record metadata."""

    pid = PersistentIdentifier()
    name = fields.List(fields.Dict(), required=True)
    organisation = fields.Dict()
    permissions = fields.Dict(dump_only=True)
    label = fields.Method('get_label')
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_record)

    def get_label(self, obj):
        """Get label."""
        return get_language_value(obj['name'])

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param dict data: Record data
        :return: Modified data
        :rtype: dict
        """
        data.pop('permissions', None)
        data.pop('label', None)

        return data

    @pre_load
    def guess_organisation(self, data, **kwargs):
        """Guess organisation from current logged user.

        :param dict data: Record data
        :return: Modified data
        :rtype: dict
        """
        # Organisation already attached to project, we do nothing.
        if data.get('organisation'):
            return data

        # Store current user organisation in new project.
        if current_user_record.get('organisation'):
            data['organisation'] = current_user_record['organisation']

        return data

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param dict item: Record data
        :return: Modified item
        :rtype: dict
        """
        item['permissions'] = {
            'read': RecordPermission.read(current_user_record, item),
            'update': RecordPermission.update(current_user_record, item),
            'delete': RecordPermission.delete(current_user_record, item)
        }

        return item


class RecordSchema(StrictKeysMixin):
    """Schema for record."""

    metadata = fields.Nested(RecordMetadataSchema)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    explanation = fields.Raw(dump_only=True)
