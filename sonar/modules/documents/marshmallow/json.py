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

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import PersistentIdentifier, \
    SanitizedUnicode
from marshmallow import fields


class DocumentMetadataSchemaV1(StrictKeysMixin):
    """Schema for the document metadata."""

    pid = PersistentIdentifier()
    type = SanitizedUnicode()
    title = fields.List(fields.Dict())
    is_part_of = SanitizedUnicode()
    abstracts = fields.List(fields.Dict())
    contribution = fields.List(fields.Dict())
    institution = fields.Dict(dump_only=True)
    _files = fields.Dict(dump_only=True)
    language = fields.List(fields.Dict())
    copyrightDate = fields.List(fields.String())
    editionStatement = fields.List(fields.Dict())
    provisionActivity = fields.List(fields.Dict())
    extent = SanitizedUnicode()
    otherMaterialCharacteristics = SanitizedUnicode()
    formats = fields.Dict()
    additionalMaterials = SanitizedUnicode()
    series = fields.List(fields.Dict())
    notes = fields.List(fields.String())
    identifiedBy = fields.List(fields.Dict())
    subjects = fields.List(fields.Dict())


class DocumentSchemaV1(StrictKeysMixin):
    """Document schema."""

    metadata = fields.Nested(DocumentMetadataSchemaV1)
    links = fields.Dict(dump_only=True)
