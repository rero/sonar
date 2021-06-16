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

"""Marshmallow for deposits."""

from __future__ import absolute_import, print_function

from functools import partial

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import fields, pre_dump, pre_load

from sonar.modules.serializers import schema_from_context
from sonar.modules.users.api import UserRecord, current_user_record
from sonar.modules.users.permissions import UserPermission

schema_from_user = partial(schema_from_context, schema=UserRecord.schema)


class UserMetadataSchemaV1(StrictKeysMixin):
    """Schema for the user metadata."""

    pid = PersistentIdentifier()
    first_name = SanitizedUnicode(required=True)
    last_name = SanitizedUnicode(required=True)
    birth_date = SanitizedUnicode()
    email = SanitizedUnicode(required=True)
    street = SanitizedUnicode()
    postal_code = SanitizedUnicode()
    city = SanitizedUnicode()
    phone = SanitizedUnicode()
    organisation = fields.Dict()
    role = SanitizedUnicode()
    full_name = SanitizedUnicode()
    subdivision = fields.Dict()
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_user)
    permissions = fields.Dict(dump_only=True)

    @pre_load
    def guess_organisation(self, data, **kwargs):
        """Guess organisation from current logged user.

        :param data: Dict of user data.
        :returns: Modified dict of user data.
        """
        # Organisation already attached to user, we do nothing.
        if data.get('organisation'):
            return data

        # Store current user organisation in new user.
        if current_user_record.get('organisation'):
            data['organisation'] = current_user_record['organisation']

        return data

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        data.pop('permissions', None)

        return data

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param data: Dict of user data.
        :returns: Modified dict of user data.
        """
        item['permissions'] = {
            'read': UserPermission.read(current_user_record, item),
            'update': UserPermission.update(current_user_record, item),
            'delete': UserPermission.delete(current_user_record, item)
        }

        return item


class UserSchemaV1(StrictKeysMixin):
    """User schema."""

    metadata = fields.Nested(UserMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    explanation = fields.Raw(dump_only=True)
