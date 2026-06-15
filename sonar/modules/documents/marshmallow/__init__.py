# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Schemas for marshmallow."""

from .json import (
    DocumentListSchemaV1,
    DocumentMetadataSchemaV1,
    DocumentReroSchemaV1,
    DocumentSchemaV1,
)

__all__ = ("DocumentListSchemaV1", "DocumentMetadataSchemaV1", "DocumentReroSchemaV1", "DocumentSchemaV1")
