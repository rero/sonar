# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""REST API of the SONAR monitoring, beside the shared monitoring of rero-invenio-base."""

from flask import Blueprint, jsonify, request
from invenio_pidstore.models import PIDStatus
from rero_invenio_base.modules.monitoring.views import check_permission

from sonar.modules.documents.urn import Urn

api_blueprint = Blueprint("sonar_monitoring", __name__, url_prefix="/monitoring")
api_blueprint.before_request(check_permission)


@api_blueprint.route("/urn")
def urn():
    """Count of unregistered urn pids.

    :return: jsonified count information.
    """
    data = {}
    try:
        days = int(args.get("days", 0)) if (args := request.args) else 0
        count, pids = Urn.get_urn_pids(days=days)
        data["reserved"] = {"count": count, "pids": list(pids)}
        count, pids = Urn.get_urn_pids(days=days, status=PIDStatus.REGISTERED)
        data["registered"] = {"count": count}
        return jsonify({"data": data})
    except Exception as exception:
        return jsonify({"error": str(exception)}), 500
