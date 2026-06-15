# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""User serializers."""

from invenio_records_rest.serializers.response import (
    record_responsify,
    search_responsify,
)

from sonar.modules.serializers import JSONSerializer as _JSONSerializer
from sonar.modules.subdivisions.api import Record as SubdivisionRecord

from ..marshmallow import UserSchemaV1


class JSONSerializer(_JSONSerializer):
    """JSON serializer for users."""

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        # Add subdivision name
        for org_term in results.get("aggregations", {}).get("subdivision", {}).get("buckets", []):
            subdivision = SubdivisionRecord.get_record_by_pid(org_term["key"])
            if subdivision:
                org_term["name"] = subdivision["name"][0]["value"]

        return super().post_process_serialize_search(results, pid_fetcher)


# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(UserSchemaV1)

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
