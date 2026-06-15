# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
            properties_order = schema.get("propertiesOrder", [])
            for field in ["isDedicated", "isShared", "arkNAAN"]:
                if field in properties_order:
                    schema["propertiesOrder"].remove(field)

        return schema
