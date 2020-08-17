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

from flask import request
from flask_security import current_user
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import fields, pre_dump, pre_load

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.permissions import DocumentPermission
from sonar.modules.documents.views import create_publication_statement, \
    dissertation, is_file_restricted, part_of_format
from sonar.modules.serializers import schema_from_context
from sonar.modules.users.api import current_user_record

schema_from_document = partial(schema_from_context,
                               schema=DocumentRecord.schema)


class FileSchemaV1(StrictKeysMixin):
    """File schema."""

    bucket = SanitizedUnicode()
    file_id = SanitizedUnicode()
    version_id = SanitizedUnicode()
    key = SanitizedUnicode()
    checksum = SanitizedUnicode()
    size = fields.Number()
    label = SanitizedUnicode()
    type = SanitizedUnicode()
    order = fields.Number()
    external_url = SanitizedUnicode()
    restricted = SanitizedUnicode()
    embargo_date = SanitizedUnicode()
    restriction = fields.Dict(dump_only=True)

    @pre_load
    def remove_restriction(self, data):
        """Remove restriction information before saving."""
        data.pop('restriction', None)
        return data


class DocumentMetadataSchemaV1(StrictKeysMixin):
    """Schema for the document metadata."""

    pid = PersistentIdentifier()
    documentType = SanitizedUnicode()
    title = fields.List(fields.Dict())
    partOf = fields.List(fields.Dict())
    abstracts = fields.List(fields.Dict())
    contribution = fields.List(fields.Dict())
    organisation = fields.Dict()
    language = fields.List(fields.Dict())
    copyrightDate = fields.List(fields.String())
    editionStatement = fields.Dict()
    provisionActivity = fields.List(fields.Dict())
    extent = SanitizedUnicode()
    otherMaterialCharacteristics = SanitizedUnicode()
    formats = fields.List(SanitizedUnicode())
    additionalMaterials = SanitizedUnicode()
    series = fields.List(fields.Dict())
    notes = fields.List(fields.String())
    identifiedBy = fields.List(fields.Dict())
    subjects = fields.List(fields.Dict())
    classification = fields.List(fields.Dict())
    specificCollections = fields.List(SanitizedUnicode())
    dissertation = fields.Dict()
    otherEdition = fields.List(fields.Dict())
    _bucket = SanitizedUnicode()
    _files = Nested(FileSchemaV1, many=True)
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_document)
    permissions = fields.Dict(dump_only=True)
    permalink = fields.Dict(dump_only=True)

    @pre_dump
    def add_files_restrictions(self, item):
        """Add restrictions to file before dumping data.

        :param item: Item object to process
        :returns: Modified item
        """
        if not item.get('_files'):
            return item

        for key, file in enumerate(item['_files']):
            if file['type'] == 'file':
                restricted = is_file_restricted(file, item)

                # Format date before serialization
                if restricted.get('date'):
                    restricted['date'] = restricted['date'].strftime(
                        '%Y-%m-%d')

                item['_files'][key]['restriction'] = restricted

        return item

    @pre_dump
    def add_permissions(self, item):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        item['permissions'] = {
            'read': DocumentPermission.read(current_user, item),
            'update': DocumentPermission.update(current_user, item),
            'delete': DocumentPermission.delete(current_user, item)
        }

        return item

    @pre_dump
    def add_permalink(self, item):
        """Add permanent link to document."""
        item['permalink'] = DocumentRecord.get_permanent_link(
            request.host_url, item['pid'])
        return item

    @pre_dump
    def add_formatted_texts(self, item):
        """Add formatted texts for objects which are processing in backend.

        :param item: Dict of record data.
        :returns: Modified data.
        """
        # Provision activity processing
        for index, provision_activity in enumerate(
                item.get('provisionActivity', [])):
            item['provisionActivity'][index][
                'text'] = create_publication_statement(provision_activity)

        # Part of proccessing
        for index, part_of in enumerate(
                item.get('partOf', [])):
            item['partOf'][index][
                'text'] = part_of_format(part_of)

        if item.get('dissertation'):
            item['dissertation']['text'] = dissertation(item)

        return item

    @pre_load
    def guess_organisation(self, data, **kwargs):
        """Guess organisation from current logged user.

        :param data: Dict of record data.
        :returns: Modified dict of record data.
        """
        # Organisation already attached to document, we do nothing.
        if data.get('organisation'):
            return data

        # Store current user organisation in new document.
        if current_user_record.get('organisation'):
            data['organisation'] = current_user_record['organisation']

        return data

    @pre_load
    def remove_formatted_texts(self, data):
        """Removes formatted texts from fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        for provision_activity in data.get('provisionActivity', []):
            provision_activity.pop('text', None)

        for part_of in data.get('partOf', []):
            part_of.pop('text', None)

        data.get('dissertation', {}).pop('text', None)


class DocumentSchemaV1(StrictKeysMixin):
    """Document schema."""

    metadata = fields.Nested(DocumentMetadataSchemaV1)
    links = fields.Dict(dump_only=True)
