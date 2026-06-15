# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Users JSON schema class."""

from flask_login import current_user

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class UsersJSONSchema(JSONSchemaBase):
    """JSON schema for users."""

    def process(self):
        """Users JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        # Remove modes fields if user does not have superuser role.
        if not current_user.is_anonymous and current_user_record:
            # Get Organisation for the current logged user
            organisation = current_user_record.replace_refs().get("organisation", {})
            # Remove some fields on json for the shared organisation
            if not organisation.get("isDedicated", False):
                for field in ["subdivision"]:
                    schema["properties"].pop(field, None)
                    if field in schema.get("propertiesOrder", []):
                        schema["propertiesOrder"].remove(field)

            if current_user_record.is_admin:
                reachable_roles = current_user_record.get_all_reachable_roles()

                schema["properties"]["role"]["widget"]["formlyConfig"]["props"]["options"] = [
                    {"label": f"role_{role}", "value": role} for role in reachable_roles
                ]
                schema["properties"]["role"]["enum"] = current_user_record.get_all_reachable_roles()
            else:
                schema["properties"].pop("role")
                if "role" in schema.get("propertiesOrder", []):
                    schema["propertiesOrder"].remove("role")

            if not current_user_record.is_superuser:
                schema["properties"].pop("organisation")
                if "organisation" in schema.get("propertiesOrder", []):
                    schema["propertiesOrder"].remove("organisation")

        return schema
