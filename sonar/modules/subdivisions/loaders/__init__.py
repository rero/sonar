# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Loaders."""

from invenio_records_rest.loaders.marshmallow import marshmallow_loader

from ..schemas import RecordMetadataSchema

#: JSON loader using Marshmallow for data validation.
json_v1 = marshmallow_loader(RecordMetadataSchema)

__all__ = ("json_v1",)
