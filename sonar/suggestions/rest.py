# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Suggestions rest views."""

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
    except Exception as err:
        endpoints = current_app.config.get("RECORDS_REST_ENDPOINTS")
        for config in endpoints.values():
            if config.get("search_index") == resource:
                search = config["search_class"]()

    if not search:
        return jsonify({"error": "Search class not found"}), 404

    results = []

    try:
        # Organisation filter for non-superusers
        if not has_superuser_access() and current_organisation:
            org_field = _ORG_FIELDS.get(resource)
            if org_field:
                search = search.filter("term", **{org_field: current_organisation["pid"]})

        for field_name in fields:
            field_search = search.query("match_phrase_prefix", **{field_name: query}).source(includes=[field_name])[:20]

            for hit in field_search.execute():
                value = hit.to_dict()
                for part in field_name.split("."):
                    if not isinstance(value, dict):
                        value = None
                        break
                    value = value.get(part)
                if isinstance(value, str):
                    results.append(value)
                elif isinstance(value, list):
                    results.extend(v for v in value if isinstance(v, str))

    except Exception:
        return jsonify({"error": "Bad request"}), 400

    # Remove duplicates
    results = list(dict.fromkeys(results))

    # Sort items
    results.sort()

    return jsonify(results)
