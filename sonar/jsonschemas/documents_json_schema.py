# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Documents JSON schema class."""

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class DocumentsJSONSchema(JSONSchemaBase):
    """JSON schema for documents."""

    def process(self):
        """Documents JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        if not current_user_record:
            return schema

        # Get Organisation for the current logged user
        organisation = current_user_record.replace_refs().get("organisation", {})
        # Remove some fields on json for the shared organisation
        if not organisation.get("isDedicated", False):
            for field in [
                "collections",
                "subdivisions",
                "customField1",
                "customField2",
                "customField3",
            ]:
                schema["properties"].pop(field, None)
                if field in schema.get("propertiesOrder", []):
                    schema["propertiesOrder"].remove(field)

        if not current_user_record.is_superuser:
            schema["properties"].pop("organisation", None)
            if "organisation" in schema.get("propertiesOrder", []):
                schema["propertiesOrder"].remove("organisation")

        return schema
