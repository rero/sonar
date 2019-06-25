# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import (
    PersistentIdentifier,
    SanitizedUnicode,
)
from marshmallow import fields


class DocumentMetadataSchemaV1(StrictKeysMixin):
    """Schema for the document metadata."""

    pid = PersistentIdentifier()
    title = SanitizedUnicode(required=True)
    abstracts = fields.List(fields.Str())
    authors = fields.Dict(dump_only=True)
    institution = fields.Dict(dump_only=True)


class DocumentSchemaV1(StrictKeysMixin):
    """Document schema."""

    metadata = fields.Nested(DocumentMetadataSchemaV1)
    # created = fields.Str(dump_only=True)
    # revision = fields.Integer(dump_only=True)
    # updated = fields.Str(dump_only=True)
    # links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
