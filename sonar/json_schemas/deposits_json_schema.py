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

"""Deposits JSON schema class."""

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class DepositsJSONSchema(JSONSchemaBase):
    """JSON schema for deposits."""

    def process(self):
        """Document JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        if current_user_record.is_moderator:
            return schema

        schema['properties']['diffusion']['properties'].pop(
            'subdivisions', None)

        return schema
