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
from invenio_records_rest.schemas.fields import PersistentIdentifier
from marshmallow import fields

from sonar.modules.serializers import schema_from_context

from .api import Record

schema_from_record = partial(schema_from_context, schema=Record.schema)


class RecordMetadataSchema(StrictKeysMixin):
    """Schema for record metadata."""

    pid = PersistentIdentifier()
    values = fields.List(fields.Dict())


class RecordSchema(StrictKeysMixin):
    """Schema for record."""

    metadata = fields.Nested(RecordMetadataSchema)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    explanation = fields.Raw(dump_only=True)
