# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Factory for creating a loader schema."""

from .archive_ouverte_unige import ArchiveOuverteUnigeSchema
from .boris import BorisSchema


class LoaderSchemaFactory:
    """Factory for creating a loader schema."""

    schemas = {
        "archive_ouverte_unige": ArchiveOuverteUnigeSchema,
        "boris": BorisSchema,
    }

    @staticmethod
    def create(schema_key):
        """Create instance of schema based on given key.

        :param schema_key: String representing the key of the schema.
        :returns: Schema instance
        """
        if LoaderSchemaFactory.schemas.get(schema_key):
            return LoaderSchemaFactory.schemas[schema_key]()

        raise Exception(f'No schema defined for key "{schema_key}"')
