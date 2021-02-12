# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Factory for creating a loader schema."""

from .crossref import CrossrefSchema
from .medline import MedlineSchema
from .unpaywall import UnpaywallSchema


class SchemaFactory():
    """Factory for creating a loader schema."""

    SCHEMAS = {
        'Medline': MedlineSchema,
        'CrossRef': CrossrefSchema,
        'unpaywall': UnpaywallSchema
    }

    @staticmethod
    def create(schema_key):
        """Create instance of schema based on given key.

        :param schema_key: String representing the key of the schema.
        :returns: Schema instance
        """
        if SchemaFactory.SCHEMAS.get(schema_key):
            return SchemaFactory.SCHEMAS[schema_key]()

        raise Exception(
            'No schema defined for key "{key}"'.format(key=schema_key))
