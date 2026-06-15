# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Factory for creating a loader schema."""

from .crossref import CrossrefSchema
from .medline import MedlineSchema
from .unpaywall import UnpaywallSchema


class SchemaFactory:
    """Factory for creating a loader schema."""

    SCHEMAS = {
        "Medline": MedlineSchema,
        "CrossRef": CrossrefSchema,
        "unpaywall": UnpaywallSchema,
    }

    @staticmethod
    def create(schema_key):
        """Create instance of schema based on given key.

        :param schema_key: String representing the key of the schema.
        :returns: Schema instance
        """
        if SchemaFactory.SCHEMAS.get(schema_key):
            return SchemaFactory.SCHEMAS[schema_key]()

        raise Exception(f'No schema defined for key "{schema_key}"')
