# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Search results."""

from invenio_records_resources.services.records.results import (
    RecordList as BaseRecordList,
)

from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.users.api import UserRecord, current_user_record


class RecordList(BaseRecordList):
    """Search list result for projects."""

    @property
    def aggregations(self):
        """Get the search result aggregations."""
        aggregations = self._results.aggregations.to_dict()

        if current_user_record:
            # Remove organisation facet for non super users
            if not current_user_record.is_superuser:
                aggregations.pop("organisation", {})

            # Remove user facet for non moderators users
            if not current_user_record.is_moderator:
                aggregations.pop("user", {})

        # Add organisation name
        for org_term in aggregations.get("organisation", {}).get("buckets", []):
            organisation = OrganisationRecord.get_record_by_pid(org_term["key"])
            if organisation:
                org_term["name"] = organisation["name"]

        # Add user name
        for org_term in aggregations.get("user", {}).get("buckets", []):
            user = UserRecord.get_record_by_pid(org_term["key"])
            if user:
                org_term["name"] = f"{user['last_name']}, {user['first_name']}"
        return aggregations
