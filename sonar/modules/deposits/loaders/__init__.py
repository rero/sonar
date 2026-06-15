# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Deposit loaders."""

from invenio_records_rest.loaders.marshmallow import marshmallow_loader

from ..marshmallow import DepositMetadataSchemaV1

json_v1 = marshmallow_loader(DepositMetadataSchemaV1)

__all__ = ("json_v1",)
