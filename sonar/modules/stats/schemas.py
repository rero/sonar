# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
