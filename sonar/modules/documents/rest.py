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

"""Documents rest views."""

from flask import Blueprint, current_app, jsonify, request

from sonar.modules.organisations.api import OrganisationRecord, current_organisation
from sonar.modules.users.api import current_user_record
from sonar.modules.utils import get_language_value

api_blueprint = Blueprint("documents", __name__, url_prefix="/documents")


@api_blueprint.route("/aggregations", methods=["GET"])
def aggregations():
    """Get aggregations list."""
    view = request.args.get("view")
    collection = request.args.get("collection")

    custom_fields = [
        "customField1",
        "customField2",
        "customField3",
    ]

    aggregations_list = [
        "document_type",
        "controlled_affiliation",
        "year",
        "collection",
        "language",
        "author",
        "subject",
        "organisation",
        "subdivision",
        *custom_fields,
    ]

    if view and view != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
        organisation = OrganisationRecord.get_record_by_pid(view)
        if organisation and organisation.get("isDedicated") and organisation.get("publicDocumentFacets"):
            aggregations_list = organisation.get("publicDocumentFacets") + custom_fields
    else:
        organisation = current_organisation

    # Remove organisation in dedicated view
    if "organisation" in aggregations_list and (
        (view and view != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"))
        or (current_user_record and not current_user_record.is_superuser)
    ):
        aggregations_list.remove("organisation")

    # Remove collection in collection context
    if collection and "collection" in aggregations_list:
        aggregations_list.remove("collection")

    # Custom fields
    for i in range(1, 4):
        # Remove custom fields if we are in global view, or the fields is not
        # configured in organisation.
        if (
            view == current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION")
            or not organisation
            or not organisation.get(f"documentsCustomField{i}", {}).get("includeInFacets")
        ):
            aggregations_list.remove(f"customField{i}")
        elif organisation[f"documentsCustomField{i}"].get("label"):
            aggregations_list[aggregations_list.index(f"customField{i}")] = {
                "key": f"customField{i}",
                "name": get_language_value(organisation[f"documentsCustomField{i}"]["label"]),
            }

    # Don't display subdivision in global context
    if view and "subdivision" in aggregations_list and view == current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
        aggregations_list.remove("subdivision")

    return jsonify(aggregations_list)
