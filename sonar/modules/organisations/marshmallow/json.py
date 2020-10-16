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
from marshmallow import fields, pre_dump

from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.organisations.permissions import OrganisationPermission
from sonar.modules.permissions import has_superuser_access
from sonar.modules.serializers import schema_from_context

schema_from_organisation = partial(schema_from_context,
                                   schema=OrganisationRecord.schema)


def can_activate_mode(value):
    """Check if current user can activate `shared` or `dedicated` mode.

    If the value is set to False, validation passed because the mode is not
    activated.

    :param value: Boolean value posted.
    :returns: True if property can be modified
    """
    return not value or has_superuser_access()


class OrganisationMetadataSchemaV1(StrictKeysMixin):
    """Schema for the organisation metadata."""

    pid = PersistentIdentifier()
    code = SanitizedUnicode(required=True)
    name = SanitizedUnicode(required=True)
    description = SanitizedUnicode()
    isShared = fields.Boolean(validate=can_activate_mode)
    isDedicated = fields.Boolean(validate=can_activate_mode)
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_organisation)
    permissions = fields.Dict(dump_only=True)
    _files = fields.List(fields.Dict())
    _bucket = SanitizedUnicode()

    @pre_dump
    def add_permissions(self, item):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        item['permissions'] = {
            'read': OrganisationPermission.read(current_user, item),
            'update': OrganisationPermission.update(current_user, item),
            'delete': OrganisationPermission.delete(current_user, item)
        }

        return item


class OrganisationSchemaV1(StrictKeysMixin):
    """organisation schema."""

    metadata = fields.Nested(OrganisationMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    explanation = fields.Raw(dump_only=True)
