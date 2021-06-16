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

from flask import request
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import EXCLUDE, fields, pre_dump, pre_load, validate

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.permissions import DocumentPermission
from sonar.modules.documents.utils import has_external_urls_for_files, \
    populate_files_properties
from sonar.modules.documents.views import contribution_text, \
    create_publication_statement, dissertation, part_of_format
from sonar.modules.serializers import schema_from_context
from sonar.modules.users.api import current_user_record

schema_from_document = partial(schema_from_context,
                               schema=DocumentRecord.schema)


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
    size = fields.Number()
    label = SanitizedUnicode()
    type = SanitizedUnicode()
    order = fields.Number()
    external_url = SanitizedUnicode()
    access = SanitizedUnicode()
    restricted_outside_organisation = fields.Boolean()
    embargo_date = SanitizedUnicode()
    restriction = fields.Dict(dump_only=True)
    links = fields.Dict(dump_only=True)
    thumbnail = SanitizedUnicode(dump_only=True)


class DocumentMetadataSchemaV1(StrictKeysMixin):
    """Schema for the document metadata."""

    pid = PersistentIdentifier()
    ark = SanitizedUnicode()
    documentType = SanitizedUnicode()
    title = fields.List(fields.Dict())
    partOf = fields.List(fields.Dict())
    abstracts = fields.List(fields.Dict())
    contribution = fields.List(fields.Dict())
    organisation = fields.List(fields.Dict())
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
    collections = fields.List(fields.Dict())
    dissertation = fields.Dict()
    otherEdition = fields.List(fields.Dict())
    usageAndAccessPolicy = fields.Dict()
    projects = fields.List(fields.Dict())
    oa_status = SanitizedUnicode()
    subdivisions = fields.List(fields.Dict())
    harvested = fields.Boolean()
    customField1 = fields.List(fields.String(validate=validate.Length(min=1)))
    customField2 = fields.List(fields.String(validate=validate.Length(min=1)))
    customField3 = fields.List(fields.String(validate=validate.Length(min=1)))
    masked = fields.Boolean()
    _bucket = SanitizedUnicode()
    _files = Nested(FileSchemaV1, many=True)
    _oai = fields.Dict()
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_document)
    permissions = fields.Dict(dump_only=True)
    permalink = SanitizedUnicode(dump_only=True)

    @pre_dump
    def populate_files_properties(self, item, **kwargs):
        """Add some customs properties to file before dumping it.

        :param item: Item object to process
        :returns: Modified item
        """
        if not item.get('_files'):
            return item

        # Check if organisation record forces to point file to an external url
        item['external_url'] = has_external_urls_for_files(item)

        # Add restriction, link and thumbnail to files
        populate_files_properties(item)

        # Sort files to have the main file in first position
        item['_files'] = sorted(item['_files'],
                                key=lambda file: file.get('order', 100))

        return item

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        # For public views, no check for permissions
        if request.args.get('view'):
            return item

        item['permissions'] = {
            'read': DocumentPermission.read(current_user_record, item),
            'update': DocumentPermission.update(current_user_record, item),
            'delete': DocumentPermission.delete(current_user_record, item)
        }

        return item

    @pre_dump
    def add_permalink(self, item, **kwargs):
        """Add permanent link to document."""
        item['permalink'] = DocumentRecord.get_permanent_link(
            request.host_url, item['pid'])
        return item

    @pre_dump
    def add_formatted_texts(self, item, **kwargs):
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
        for index, part_of in enumerate(item.get('partOf', [])):
            item['partOf'][index]['text'] = part_of_format(part_of)

        # Contribution
        for index, contribution in enumerate(item.get('contribution', [])):
            item['contribution'][index]['text'] = contribution_text(
                contribution)

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
            data['organisation'] = [current_user_record['organisation']]

        return data

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        for provision_activity in data.get('provisionActivity', []):
            provision_activity.pop('text', None)

        for part_of in data.get('partOf', []):
            part_of.pop('text', None)

        for contribution in data.get('contribution', []):
            contribution.pop('text', None)

        data.get('dissertation', {}).pop('text', None)

        data.pop('permalink', None)
        data.pop('permissions', None)

        return data


class DocumentSchemaV1(StrictKeysMixin):
    """Document schema."""

    id = PersistentIdentifier()
    metadata = fields.Nested(DocumentMetadataSchemaV1)
    links = fields.Dict(dump_only=True)
    explanation = fields.Raw(dump_only=True)
