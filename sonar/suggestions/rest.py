# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Suggestions rest views."""

from elasticsearch_dsl.query import Q
from flask import Blueprint, current_app, jsonify, request

from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import has_superuser_access, is_user_logged_and_submitter
from sonar.proxies import sonar
from sonar.suggestions.dumpers import FIELD

api_blueprint = Blueprint("suggestions", __name__, url_prefix="/suggestions")

# Organisation filter field per resource, using ES double-underscore path notation.
_ORG_FIELDS = {
    "projects": "metadata__organisation__pid",
    "documents": "organisation__pid",
}


@api_blueprint.route("/completion", methods=["GET"])
@is_user_logged_and_submitter
def completion():
    """Suggestions completion."""
    query = request.args.get("q")
    field = request.args.get("field")
    resource = request.args.get("resource")

    if not query:
        return jsonify({"error": "No query parameter given"}), 400

    if not field:
        return jsonify({"error": "No field parameter given"}), 400

    if not resource:
        return jsonify({"error": "No resource parameter given"}), 400

    search = None
    try:
        service = sonar.service(resource)
        search = service.config.search.search_cls(index=resource)
    except AttributeError:
        # `sonar.service()` returns None for resources without a service,
        # fall back on the REST endpoints.
        endpoints = current_app.config.get("RECORDS_REST_ENDPOINTS")
        for config in endpoints.values():
            if config.get("search_index") == resource:
                search = config["search_class"]()

    if not search:
        return jsonify({"error": "Search class not found"}), 404

    # Organisation filter for non-superusers
    if not has_superuser_access() and current_organisation and (org_field := _ORG_FIELDS.get(resource)):
        search = search.filter("term", **{org_field: current_organisation["pid"]})

    # The dumper indexes each suggestable value as its own nested object, so the
    # aggregation returns the matching values only, ordered by the number of
    # records they appear in. Each typed word must be an indexed n-gram of the
    # same value, so partial words match without the term expansion a prefix
    # query would need.
    matching = Q("terms", **{f"{FIELD}.field": field.split(",")}) & Q(
        "match", **{f"{FIELD}.value": {"query": query, "operator": "and"}}
    )

    # The same query selects the records first, so the aggregation walks the
    # values of the matching records instead of the whole index. A resource
    # without suggestable values has no `suggestions` mapping and, thanks to
    # `ignore_unmapped`, returns no suggestion instead of an error.
    search = search.filter("nested", path=FIELD, query=matching, ignore_unmapped=True).extra(size=0)
    search.aggs.bucket(FIELD, "nested", path=FIELD).bucket("matching", "filter", filter=matching).bucket(
        "values",
        "terms",
        field=f"{FIELD}.value.raw",
        size=current_app.config["SONAR_APP_SUGGESTIONS_MAX_RESULTS"],
        shard_size=current_app.config["SONAR_APP_SUGGESTIONS_SHARD_SIZE"],
    )

    results = search.execute()

    return jsonify([bucket.key for bucket in results.aggregations[FIELD].matching.values.buckets])
