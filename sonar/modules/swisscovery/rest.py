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

"""Swisscovery rest views."""

import re

import requests
import xmltodict
from flask import Blueprint, current_app, jsonify, request

from sonar.modules.deposits.serializers.schemas.document import (
    DocumentSchema as DepositDocumentSchema,
)
from sonar.modules.documents.loaders.schemas.sru import SRUSchema
from sonar.modules.permissions import is_user_logged_and_submitter

api_blueprint = Blueprint("swisscovery", __name__, url_prefix="/swisscovery")


@api_blueprint.route("/", methods=["GET"])
@is_user_logged_and_submitter
def get_record():
    """Get record."""
    search_type = request.args.get("type", "all_for_ui")
    query = request.args.get("query")
    fmt = request.args.get("format", "document")

    if not search_type or not query:
        return jsonify({}), 400

    params = {
        "operation": "searchRetrieve",
        "version": current_app.config.get("SONAR_APP_SWISSCOVERY_SEARCH_VERSION"),
        "recordSchema": "marcxml",
        "maximumRecords": "1",
        "startRecord": "1",
        "query": f'({search_type}="{query}")',
    }
    response = requests.get(current_app.config.get("SONAR_APP_SWISSCOVERY_SEARCH_URL"), params=params)
    result = xmltodict.parse(response.text)

    if not result["sru:searchRetrieveResponse"].get("sru:records") or not result["sru:searchRetrieveResponse"][
        "sru:records"
    ].get("sru:record"):
        return jsonify({}), 200

    # Get only relevant XML part.
    record = xmltodict.unparse(
        result["sru:searchRetrieveResponse"]["sru:records"]["sru:record"]["sru:recordData"],
        full_document=False,
    )

    record = SRUSchema().dump(record)

    # Regular expression to remove the << and >> around a value in the title
    # Ex: <<La>> vie est belle => La vie est belle
    pattern = re.compile("<<(.+)>>", re.S)
    for title in record.get("title", []):
        for main_title in title.get("mainTitle", []):
            main_title["value"] = re.sub(pattern, r"\1", main_title["value"])

    # Serialize for deposit.
    if fmt == "deposit":
        record = DepositDocumentSchema().dump(record)

    return jsonify(record)
