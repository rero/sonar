# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Deposit serializers."""

from invenio_records_rest.serializers.response import (
    record_responsify,
    search_responsify,
)

from sonar.modules.serializers import JSONSerializer as _JSONSerializer
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.users.api import UserRecord

from ..marshmallow import DepositSchemaV1


class JSONSerializer(_JSONSerializer):
    """JSON serializer for projects."""

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        # Add user name
        for org_term in results.get("aggregations", {}).get("user", {}).get("buckets", []):
            user = UserRecord.get_record_by_pid(org_term["key"])
            if user:
                org_term["name"] = f"{user['last_name']}, {user['first_name']}"
        # Add subdivision name
        for org_term in results.get("aggregations", {}).get("subdivision", {}).get("buckets", []):
            subdivision = SubdivisionRecord.get_record_by_pid(org_term["key"])
            if subdivision:
                org_term["name"] = subdivision["name"][0]["value"]

        return super().post_process_serialize_search(results, pid_fetcher)


# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(DepositSchemaV1)

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, "application/json")
#: JSON record serializer for search results.
json_v1_search = search_responsify(json_v1, "application/json")

__all__ = (
    "json_v1",
    "json_v1_response",
    "json_v1_search",
)
