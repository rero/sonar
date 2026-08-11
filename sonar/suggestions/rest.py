# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Suggestions rest views."""

import re
import unicodedata

from elasticsearch.exceptions import RequestError
from flask import Blueprint, current_app, jsonify, request

from sonar.modules.organisations.api import current_organisation
from sonar.modules.permissions import has_superuser_access, is_user_logged_and_submitter
from sonar.proxies import sonar

api_blueprint = Blueprint("suggestions", __name__, url_prefix="/suggestions")

# Organisation filter field per resource, using ES double-underscore path notation.
_ORG_FIELDS = {
    "projects": "metadata__organisation__pid",
    "documents": "organisation__pid",
}

# Sub-field holding the edge n-grams, see the `autocomplete` analyzer in the
# `record.json` ES template. Queries target it, values are read back from the
# parent field as sub-fields are not part of the `_source`.
_SUGGEST_SUFFIX = ".suggest"

# Documents inspected per field, and suggestions finally returned.
_MAX_HITS = 50
_MAX_RESULTS = 20


def _source_field(field_name):
    """Return the `_source` path of a queried field.

    :param field_name: queried field, ie. `contribution.agent.preferred_name.suggest`.
    :returns: the path holding the value, ie. `contribution.agent.preferred_name`.
    """
    if field_name.endswith(_SUGGEST_SUFFIX):
        return field_name[: -len(_SUGGEST_SUFFIX)]

    return field_name


def _extract_values(source, parts):
    """Collect the string values reachable through a field path.

    Lists are walked at any level, as arrays of objects are common in the
    schemas, ie. `contribution.agent.preferred_name`.

    :param source: portion of the `_source` to walk.
    :param parts: remaining parts of the field path.
    :returns: generator over the string values found.
    """
    if isinstance(source, list):
        for item in source:
            yield from _extract_values(item, parts)
    elif not parts:
        if isinstance(source, str):
            yield source
    elif isinstance(source, dict):
        yield from _extract_values(source.get(parts[0]), parts[1:])


def _words(value):
    """Split a value into lowercased words, without diacritics.

    :param value: value to split.
    :returns: list of words.
    """
    decomposed = unicodedata.normalize("NFKD", value.lower())
    folded = "".join(char for char in decomposed if not unicodedata.combining(char))

    return re.findall(r"\w+", folded)


def _matches(value, query):
    """Check that a value matches the typed query.

    Elasticsearch matches a record as a whole, so a hit carries every value of
    the field, including those the user did not type. Keep only the values for
    which each typed word is the prefix of a word.

    Diacritics are ignored, so that a value legitimately matched by Elasticsearch
    is never discarded here.

    :param value: value to check.
    :param query: query typed by the user.
    :returns: True if the value matches the query.
    """
    words = _words(value)

    return all(any(word.startswith(term) for word in words) for term in _words(query))


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

    fields = field.split(",")

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

    results = []

    try:
        # Organisation filter for non-superusers
        if not has_superuser_access() and current_organisation and (org_field := _ORG_FIELDS.get(resource)):
            search = search.filter("term", **{org_field: current_organisation["pid"]})

        for field_name in fields:
            source_field = _source_field(field_name)
            # Each typed word must be an indexed n-gram, so partial words match
            # without the term expansion a prefix query would need.
            field_search = search.query("match", **{field_name: {"query": query, "operator": "and"}})
            field_search = field_search.source(includes=[source_field])[:_MAX_HITS]

            for hit in field_search.execute():
                results.extend(
                    value for value in _extract_values(hit.to_dict(), source_field.split(".")) if _matches(value, query)
                )

    except RequestError:
        return jsonify({"error": "Bad request"}), 400

    results = sorted(dict.fromkeys(results))
    return jsonify(results[:_MAX_RESULTS])
