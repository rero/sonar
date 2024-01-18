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

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from functools import partial

from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import EXCLUDE, fields, pre_dump, pre_load

from sonar.modules.organisations.api import OrganisationRecord, \
    current_organisation
from sonar.modules.organisations.permissions import \
    OrganisationFilesPermission, OrganisationPermission
from sonar.modules.permissions import has_superuser_access
from sonar.modules.serializers import schema_from_context
from sonar.modules.users.api import current_user_record

schema_from_organisation = partial(schema_from_context,
                                   schema=OrganisationRecord.schema)

class FileSchemaV1(StrictKeysMixin):
    """File schema."""

    class Meta:
        """Meta for file schema."""

        # Specifically exclude unknown fields, as in the new version of
        # marshmallow, dump_only fields are treated as included.
        # https://github.com/marshmallow-code/marshmallow/issues/875
        unknown = EXCLUDE

    bucket = SanitizedUnicode()
    file_id = SanitizedUnicode()
    version_id = SanitizedUnicode()
    key = SanitizedUnicode()
    mimetype = SanitizedUnicode()
    checksum = SanitizedUnicode()
    size = fields.Integer()
    label = SanitizedUnicode()
    type = SanitizedUnicode()
    order = fields.Integer()
    external_url = SanitizedUnicode()
    access = SanitizedUnicode()
    restricted_outside_organisation = fields.Boolean()
    embargo_date = SanitizedUnicode()
    restriction = fields.Dict(dump_only=True)
    links = fields.Dict(dump_only=True)
    thumbnail = SanitizedUnicode(dump_only=True)
    permissions = fields.Dict(dump_only=True)

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        if not item.get('bucket'):
            return item
        doc = OrganisationRecord.get_record_by_bucket(item.get('bucket'))
        item['permissions'] = {
            'read': OrganisationFilesPermission.read(current_user_record, item, doc['pid'], doc),
            'update': OrganisationFilesPermission.update(current_user_record, item, doc['pid'], doc),
            'delete': OrganisationFilesPermission.delete(current_user_record, item, doc['pid'], doc)
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

class OrganisationMetadataSchemaV1(StrictKeysMixin):
    """Schema for the organisation metadata."""

    pid = PersistentIdentifier()
    code = SanitizedUnicode(required=True)
    name = SanitizedUnicode(required=True)
    description = fields.List(fields.Dict())
    footer = fields.List(fields.Dict())
    isShared = fields.Boolean()
    isDedicated = fields.Boolean()
    serverName = fields.Str()
    allowedIps = SanitizedUnicode()
    arkNAAN = SanitizedUnicode()
    platformName = SanitizedUnicode()
    documentsCustomField1 = fields.Dict()
    documentsCustomField2 = fields.Dict()
    documentsCustomField3 = fields.Dict()
    publicDocumentFacets = fields.List(fields.String())
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_organisation)
    permissions = fields.Dict(dump_only=True)
    _files = Nested(FileSchemaV1, many=True)
    _bucket = SanitizedUnicode()

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        item['permissions'] = {
            'read': OrganisationPermission.read(current_user_record, item),
            'update': OrganisationPermission.update(current_user_record, item),
            'delete': OrganisationPermission.delete(current_user_record, item)
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

    @pre_load
    def override_modes(self, data, **kwargs):
        """Override organisation's modes.

        For non super users, the modes (isShared, isDedicated) is not saved
        by posting the data, but guessed from user's organisation.
        """
        if not has_superuser_access():
            data['isShared'] = current_organisation.get('isShared', False)
            data['isDedicated'] = current_organisation.get(
                'isDedicated', False)
        return data

    @pre_load
    def override_ark_naan(self, data, **kwargs):
        """Override ARK naan.

        For non super users, the NAAN ark is not saved
        by posting the data, but guessed from user's organisation.
        """
        if not has_superuser_access():
            if arkNAAN := current_organisation.get('arkNAAN'):
                data['arkNAAN'] = arkNAAN
            else:
                data.pop('arkNAAN', None)
        return data


class OrganisationSchemaV1(StrictKeysMixin):
    """organisation schema."""

    metadata = fields.Nested(OrganisationMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    explanation = fields.Raw(dump_only=True)
