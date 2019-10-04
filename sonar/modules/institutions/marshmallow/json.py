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

from invenio_jsonschemas.proxies import current_jsonschemas
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import fields, missing, validate


class InstitutionMetadataSchemaV1(StrictKeysMixin):
    """Schema for the institution metadata."""

    pid = PersistentIdentifier()
    name = SanitizedUnicode(required=True)


class InstitutionSchemaV1(StrictKeysMixin):
    """Institution schema."""

    metadata = fields.Nested(InstitutionMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
