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

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import fields, pre_dump

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.views import is_file_restricted
from sonar.modules.serializers import schema_from_context

schema_from_document = partial(schema_from_context,
                               schema=DocumentRecord.schema)


class DocumentMetadataSchemaV1(StrictKeysMixin):
    """Schema for the document metadata."""

    pid = PersistentIdentifier()
    documentType = SanitizedUnicode()
    title = fields.List(fields.Dict())
    partOf = fields.List(fields.Dict())
    abstracts = fields.List(fields.Dict())
    contribution = fields.List(fields.Dict())
    organisation = fields.Dict(dump_only=True)
    _files = fields.Dict(dump_only=True)
    language = fields.List(fields.Dict())
    copyrightDate = fields.List(fields.String())
    editionStatement = fields.Dict()
    provisionActivity = fields.List(fields.Dict())
    extent = SanitizedUnicode()
    otherMaterialCharacteristics = SanitizedUnicode()
    formats = fields.Dict()
    additionalMaterials = SanitizedUnicode()
    series = fields.List(fields.Dict())
    notes = fields.List(fields.String())
    identifiedBy = fields.List(fields.Dict())
    subjects = fields.List(fields.Dict())
    classification = fields.List(fields.Dict())
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_document)

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

                item['_files'][key]['restricted'] = restricted

        return item


class DocumentSchemaV1(StrictKeysMixin):
    """Document schema."""

    metadata = fields.Nested(DocumentMetadataSchemaV1)
    links = fields.Dict(dump_only=True)
