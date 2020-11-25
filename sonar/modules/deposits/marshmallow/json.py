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

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from functools import partial

from flask_security import current_user
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import fields, pre_dump, pre_load

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.deposits.permissions import DepositPermission
from sonar.modules.serializers import schema_from_context

schema_from_deposit = partial(schema_from_context, schema=DepositRecord.schema)


class DepositMetadataSchemaV1(StrictKeysMixin):
    """Schema for the deposit metadata."""

    pid = PersistentIdentifier()
    contributors = fields.List(fields.Dict())
    diffusion = fields.Dict()
    document = fields.Dict()
    logs = fields.List(fields.Dict())
    metadata = fields.Dict()
    status = SanitizedUnicode()
    step = SanitizedUnicode()
    user = fields.Dict()
    projects = fields.List(fields.Dict())
    _files = fields.List(fields.Dict())
    _bucket = SanitizedUnicode()
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_deposit)
    permissions = fields.Dict(dump_only=True)

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record
        :returns: Dict of modified record.
        """
        item['permissions'] = {
            'read': DepositPermission.read(current_user, item),
            'update': DepositPermission.update(current_user, item),
            'delete': DepositPermission.delete(current_user, item)
        }

        return item

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        data.pop('permissions', None)

        return data


class DepositSchemaV1(StrictKeysMixin):
    """Deposit schema."""

    metadata = fields.Nested(DepositMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    explanation = fields.Raw(dump_only=True)
