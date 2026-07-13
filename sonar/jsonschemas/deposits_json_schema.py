# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Deposits JSON schema class."""

from flask import current_app

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class DepositsJSONSchema(JSONSchemaBase):
    """JSON schema for deposits."""

    def process(self):
        """Document JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        organisation = {}
        if current_user_record:
            organisation = current_user_record.replace_refs().get("organisation")

        if organisation.get("code") in current_app.config.get(
            "SONAR_APP_DEPOSITS_DISABLE_NEW_PROJECT_ORGANISATIONS", []
        ):
            schema["properties"]["projects"]["items"]["oneOf"].pop(1)

        if not current_user_record or (current_user_record.is_moderator and organisation.get("isDedicated", False)):
            return schema

        # Remove some fields on json for the shared organisation
        if not organisation.get("isDedicated", False):
            # Remove fields for shared organisation
            for field in [
                "collections",
                "customField1",
                "customField2",
                "customField3",
            ]:
                schema["properties"]["metadata"]["properties"].pop(field, None)
                properties_order = schema["properties"]["metadata"].get("propertiesOrder", [])
                if field in properties_order:
                    properties_order.remove(field)

        # Remove subdivisions field
        schema["properties"]["diffusion"]["properties"].pop("subdivisions", None)
        properties_order = schema["properties"]["diffusion"].get("propertiesOrder", [])
        if "subdivisions" in properties_order:
            schema["properties"]["diffusion"]["propertiesOrder"].remove("subdivisions")

        return schema
