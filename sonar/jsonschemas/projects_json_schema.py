# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Projects JSON schema class."""

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class ProjectsJSONSchema(JSONSchemaBase):
    """JSON schema for projects."""

    def process(self):
        """Projects JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()
        # Remove modes fields if user does not have superuser role.
        if current_user_record and not current_user_record.is_superuser:
            schema["properties"]["metadata"]["properties"].pop("organisation", None)
            if "organisation" in schema["properties"]["metadata"]["propertiesOrder"]:
                schema["properties"]["metadata"]["propertiesOrder"].remove("organisation")

        return schema
