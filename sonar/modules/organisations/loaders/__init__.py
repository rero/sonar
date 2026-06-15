# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Loaders.

This file contains sample loaders that can be used to deserialize input data in
an application level data structure. The marshmallow_loader() method can be
parameterized with different schemas for the record metadata. In the provided
json_v1 instance, it uses the OrganisationMetadataSchemaV1, defining the
PersistentIdentifier field.
"""

from invenio_records_rest.loaders.marshmallow import marshmallow_loader

from ..marshmallow import OrganisationMetadataSchemaV1

#: JSON loader using Marshmallow for data validation.
json_v1 = marshmallow_loader(OrganisationMetadataSchemaV1)

__all__ = ("json_v1",)
