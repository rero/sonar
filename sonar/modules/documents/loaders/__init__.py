# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Document loaders."""

from __future__ import absolute_import, print_function

from invenio_records_rest.loaders.marshmallow import (
    json_patch_loader,
    marshmallow_loader,
)

from ..marshmallow import DocumentMetadataSchemaV1

json_v1 = marshmallow_loader(DocumentMetadataSchemaV1)

__all__ = ("json_v1",)
