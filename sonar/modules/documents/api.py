# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Document Api."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_jsonschemas import current_jsonschemas
from invenio_records.api import Record


class DocumentRecord(Record):
    """Document record class."""

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create Document record."""
        data["$schema"] = current_jsonschemas.path_to_url(
                'documents/document-v1.0.0.json')
        return super(DocumentRecord, cls).create(data, id_=id_, **kwargs)
