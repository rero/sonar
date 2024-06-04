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

"""Factory for JSON schema."""

from .deposits_json_schema import DepositsJSONSchema
from .documents_json_schema import DocumentsJSONSchema
from .json_schema_base import JSONSchemaBase
from .organisations_json_schema import OrganisationsJSONSchema
from .projects_json_schema import ProjectsJSONSchema
from .users_json_schema import UsersJSONSchema


class JSONSchemaFactory:
    """Factory for JSON schema."""

    SCHEMAS = {
        "deposits": DepositsJSONSchema,
        "documents": DocumentsJSONSchema,
        "organisations": OrganisationsJSONSchema,
        "projects": ProjectsJSONSchema,
        "users": UsersJSONSchema,
    }

    @staticmethod
    def create(resource_type):
        """Create instance of schema based on the given resource.

        :param resource_type: String representing the type of resource.
        :returns: The schema instance.
        """
        if JSONSchemaFactory.SCHEMAS.get(resource_type):
            return JSONSchemaFactory.SCHEMAS[resource_type](resource_type)

        return JSONSchemaBase(resource_type)
