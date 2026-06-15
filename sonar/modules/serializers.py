# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""JSON serializer for SONAR."""

import json

from flask import request
from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.serializers.json import JSONSerializer as _JSONSerializer

from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.utils import get_language_value


class JSONSerializer(_JSONSerializer):
    """JSON serializer for SONAR."""

    @staticmethod
    def preprocess_search_hit(pid, record_hit, links_factory=None, **kwargs):
        """Prepare a record hit from Elasticsearch for serialization."""
        record = super(JSONSerializer, JSONSerializer).preprocess_search_hit(
            pid=pid, record_hit=record_hit, links_factory=links_factory, kwargs=kwargs
        )

        # Adds explanation of how elasticsearch attributes relevances on hits.
        if record_hit.get("_explanation"):
            record["explanation"] = record_hit.get("_explanation")

        return record

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        """Prepare record for serialization."""
        if request and request.args.get("resolve") == "1":
            record = record.resolve()

        return super().preprocess_record(pid=pid, record=record, links_factory=links_factory, kwargs=kwargs)

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        # Add subdivision name
        for org_term in results.get("aggregations", {}).get("subdivision", {}).get("buckets", []):
            subdivision = SubdivisionRecord.get_record_by_pid(org_term["key"])
            if subdivision:
                org_term["name"] = get_language_value(subdivision["name"])

        return results

    def serialize_search(self, pid_fetcher, search_result, links=None, item_links_factory=None, **kwargs):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        results = {
            "hits": {
                "hits": [
                    self.transform_search_hit(
                        pid_fetcher(hit["_id"], hit["_source"]),
                        hit,
                        links_factory=item_links_factory,
                        **kwargs,
                    )
                    for hit in search_result["hits"]["hits"]
                ],
                "total": search_result["hits"]["total"],
            },
            "links": links or {},
            "aggregations": search_result.get("aggregations", {}),
        }
        return json.dumps(
            self.post_process_serialize_search(results, pid_fetcher),
            **self._format_args(),
        )


def schema_from_context(_, context, data, schema):
    """Get the record's schema from context."""
    record = (context or {}).get("record", {})

    return record.get("$schema", current_jsonschemas.path_to_url(schema))
