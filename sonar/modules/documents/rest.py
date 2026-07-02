# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Documents rest views."""

from flask import Blueprint, current_app, jsonify, request

from sonar.modules.documents.citations import citation_registry
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


@api_blueprint.route("/citation-styles", methods=["GET"])
def citation_styles():
    """Return the list of supported citation styles."""
    return jsonify(citation_registry.styles_info())


@api_blueprint.route("/<pid_value>/citation", methods=["GET"])
def citation(pid_value):
    """Return a formatted bibliographic citation for a document."""
    from sonar.modules.documents.api import DocumentRecord

    style = request.args.get("style", "apa_7")
    lang = request.args.get("lang")

    if style not in citation_registry.supported_styles:
        return (
            jsonify(
                {
                    "message": f"Unsupported style '{style}'. Choose from: {', '.join(citation_registry.supported_styles)}"
                }
            ),
            400,
        )

    record = DocumentRecord.get_record_by_pid(pid_value)
    if record is None:
        return jsonify({"message": "Document not found"}), 404

    from sonar.modules.documents.permissions import DocumentPermission

    if not DocumentPermission.read(current_user_record, record):
        if not current_user_record:
            return jsonify({"message": "Authentication required"}), 401
        return jsonify({"message": "Permission denied"}), 403

    try:
        citation_text = citation_registry.format(record, style, lang=lang, host_url=request.host_url)
    except AttributeError, UnboundLocalError:
        # citeproc-py can raise these deep inside its own rendering code on
        # unexpected CSL data (e.g. a style/field combination it doesn't
        # support, see the citations.registry module docstring), rather than
        # a bug in our own mapping.
        current_app.logger.exception("Citation rendering failed for document %s (style=%s)", pid_value, style)
        return jsonify({"message": "Citation could not be generated for this document."}), 500

    return jsonify({"citation": citation_text})
