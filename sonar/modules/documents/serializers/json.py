# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Dublin Core REST serializer."""

from datetime import datetime

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.serializers import JSONSerializer as BasedJSONSerializer
from sonar.modules.utils import get_language_value


class JSONSerializer(BasedJSONSerializer):
    """JSON serializer for documents."""

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        if results["aggregations"].get("year"):
            results["aggregations"]["year"]["type"] = "range"
            results["aggregations"]["year"]["config"] = {
                "min": 1950,
                "max": int(datetime.now().year),
                "step": 1,
            }

        # Add organisation name
        for org_term in results.get("aggregations", {}).get("organisation", {}).get("buckets", []):
            if organisation := OrganisationRecord.get_record_by_pid(org_term["key"]):
                org_term["name"] = organisation["name"]

        # Add collection name
        for org_term in results.get("aggregations", {}).get("collection", {}).get("buckets", []):
            if collection := CollectionRecord.get_record_by_pid(org_term["key"]):
                org_term["name"] = get_language_value(collection["name"])
        return super().post_process_serialize_search(results, pid_fetcher)
