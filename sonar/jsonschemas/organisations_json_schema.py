# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Organisations JSON schema class."""

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class OrganisationsJSONSchema(JSONSchemaBase):
    """JSON schema for organisations."""

    def process(self):
        """Organisations JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        # Remove modes fields if user does not have superuser role.
        if not current_user_record.is_superuser:
            propertiesOrder = schema.get("propertiesOrder", [])
            for field in ["isDedicated", "isShared", "arkNAAN"]:
                if field in propertiesOrder:
                    schema["propertiesOrder"].remove(field)

        return schema
