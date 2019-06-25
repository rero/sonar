# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import (
    PersistentIdentifier,
    SanitizedUnicode,
)
from marshmallow import fields


class InstitutionMetadataSchemaV1(StrictKeysMixin):
    """Schema for the institution metadata."""

    pid = PersistentIdentifier()
    name = SanitizedUnicode(required=True)
    key = SanitizedUnicode(required=True)


class InstitutionSchemaV1(StrictKeysMixin):
    """Institution schema."""

    metadata = fields.Nested(InstitutionMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
