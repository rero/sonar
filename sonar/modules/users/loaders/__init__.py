# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Loaders for users."""

from invenio_records_rest.loaders.marshmallow import marshmallow_loader

from ..marshmallow import UserMetadataSchemaV1

#: JSON loader using Marshmallow for data validation.
json_v1 = marshmallow_loader(UserMetadataSchemaV1)

__all__ = ("json_v1",)
