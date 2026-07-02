# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Documents rest views."""

from datetime import UTC, datetime

from flask import Blueprint, Response, current_app, jsonify, request
from werkzeug.utils import secure_filename

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


@api_blueprint.route("/<pid_value>/export/<fmt>", methods=["GET"])
def export(pid_value, fmt):
    """Export a document record in the requested format as a downloadable file.

    :param pid_value: Document PID.
    :param fmt: Format alias (json, dc, bibtex, ris).
    """
    from invenio_pidstore.errors import PIDDoesNotExistError
    from invenio_pidstore.models import PersistentIdentifier
    from sqlalchemy.exc import SQLAlchemyError

    from sonar.modules.documents.api import DocumentRecord
    from sonar.modules.documents.serializers import bibtex_v1, dc_v1, json_v1, ris_v1

    formats = {
        "json": (json_v1, "application/json", ".json"),
        "dc": (dc_v1, "text/xml", ".xml"),
        "bibtex": (bibtex_v1, "application/x-bibtex", ".bib"),
        "ris": (ris_v1, "application/x-research-info-systems", ".ris"),
    }

    if fmt not in formats:
        return jsonify({"message": f"Unsupported format '{fmt}'. Choose from: {', '.join(formats)}"}), 400

    try:
        pid = PersistentIdentifier.get(DocumentRecord.provider.pid_type, pid_value)
        record = DocumentRecord.get_record_by_pid(pid_value)
    except PIDDoesNotExistError:
        return jsonify({"message": "Document not found"}), 404
    except SQLAlchemyError:
        current_app.logger.exception("Unexpected DB error while resolving document %s", pid_value)
        raise

    if record is None:
        return jsonify({"message": "Document not found"}), 404

    serializer, mimetype, extension = formats[fmt]
    body = serializer.serialize(pid, record)
    today = datetime.now(UTC).strftime("%Y%m%d")
    safe_pid_value = secure_filename(pid_value)

    return Response(
        body,
        mimetype=mimetype,
        headers={"Content-Disposition": f"attachment; filename={today}-{safe_pid_value}{extension}"},
    )
