# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
    def create(resource_type, with_refs=False):
        """Create instance of schema based on the given resource.

        :param resource_type: String representing the type of resource.
        :returns: The schema instance.
        """
        if json_schema_cls := JSONSchemaFactory.SCHEMAS.get(resource_type):
            return json_schema_cls(resource_type, with_refs)

        return JSONSchemaBase(resource_type, with_refs)
