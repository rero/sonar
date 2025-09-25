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

"""Deposit rest views."""

from datetime import datetime

from flask import Blueprint, abort, current_app, jsonify, make_response, request
from flask_babel import _
from invenio_db import db

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.pdf_extractor.pdf_extractor import PDFExtractor
from sonar.modules.pdf_extractor.utils import format_extracted_data
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.users.api import UserRecord
from sonar.modules.utils import get_language_value, send_email

api_blueprint = Blueprint("deposits", __name__, url_prefix="/deposits/<pid>/", template_folder="templates")


@api_blueprint.route("/publish", methods=["POST"])
def publish(pid=None):
    """Publish a deposit or send a message for review."""
    deposit = DepositRecord.get_record_by_pid(pid)

    if (
        not deposit
        or deposit["step"] != DepositRecord.STEP_DIFFUSION
        or deposit["status"] not in [DepositRecord.STATUS_IN_PROGRESS, DepositRecord.STATUS_ASK_FOR_CHANGES]
    ):
        abort(400)

    user = UserRecord.get_record_by_ref_link(deposit["user"]["$ref"])

    # Deposit can be validated directly
    if user.is_granted(UserRecord.ROLE_MODERATOR):
        deposit["status"] = DepositRecord.STATUS_VALIDATED

        # Create document based on deposit
        deposit.create_document()
    else:
        deposit["status"] = DepositRecord.STATUS_TO_VALIDATE

        subdivision = (
            SubdivisionRecord.get_record_by_ref_link(user["subdivision"]["$ref"]) if user.get("subdivision") else None
        )

        moderators_emails = user.get_moderators_emails(subdivision["pid"] if subdivision else None)

        email_subject = _("Deposit to validate")
        if subdivision:
            email_subject += f" ({get_language_value(subdivision['name'])})"

        if moderators_emails:
            # Send an email to validators
            send_email(
                moderators_emails,
                email_subject,
                "deposits/email/validation",
                {
                    "deposit": deposit,
                    "user": user,
                    "link": current_app.config.get("SONAR_APP_ANGULAR_URL"),
                },
                False,
            )

    deposit.log_action(user, "submit")

    deposit.commit()
    deposit.reindex()
    db.session.commit()

    return make_response()


@api_blueprint.route("/review", methods=["POST"])
def review(pid=None):
    """Review a deposit and change the deposit status depending on action."""
    deposit = DepositRecord.get_record_by_pid(pid)

    if not deposit or deposit["status"] != DepositRecord.STATUS_TO_VALIDATE:
        abort(400)

    payload = request.get_json()

    if not payload:
        abort(400)

    if (
        "action" not in payload
        or "user" not in payload
        or payload["action"]
        not in [
            DepositRecord.REVIEW_ACTION_APPROVE,
            DepositRecord.REVIEW_ACTION_REJECT,
            DepositRecord.REVIEW_ACTION_ASK_FOR_CHANGES,
        ]
    ):
        abort(400)

    user = UserRecord.get_record_by_ref_link(payload["user"]["$ref"])

    if not user or not user.is_moderator:
        abort(403)

    subject = None
    status = None

    if payload["action"] == DepositRecord.REVIEW_ACTION_APPROVE:
        subject = _("Deposit approval")
        status = DepositRecord.STATUS_VALIDATED

        # Create document based on deposit
        deposit.create_document()
    elif payload["action"] == DepositRecord.REVIEW_ACTION_REJECT:
        subject = _("Deposit rejection")
        status = DepositRecord.STATUS_REJECTED
    else:
        subject = _("Ask for changes on deposit")
        status = DepositRecord.STATUS_ASK_FOR_CHANGES

    deposit["status"] = status

    # Log action
    deposit.log_action(payload["user"], payload["action"], payload["comment"])

    # Load user who creates the deposit
    deposit_user = UserRecord.get_record_by_ref_link(deposit["user"]["$ref"])

    send_email(
        [deposit_user["email"]],
        subject,
        f"deposits/email/{payload['action']}",
        {
            "deposit": deposit,
            "deposit_user": deposit_user,
            "user": user,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "comment": payload["comment"],
            "link": current_app.config.get("SONAR_APP_ANGULAR_URL"),
        },
        False,
    )

    deposit.commit()
    deposit.reindex()
    db.session.commit()

    return make_response(jsonify(deposit))


@api_blueprint.route("/extract-pdf-metadata", methods=["GET"])
def extract_metadata(pid=None):
    """Publish a deposit or send a message for review."""
    deposit = DepositRecord.get_record_by_pid(pid)

    if not deposit:
        abort(400)
    # TODO: check if order should be required
    main_file = [file for file in deposit.files if file.get("order") == 1 and file.mimetype == "application/pdf"]

    if not main_file:
        abort(500)

    # Get file content
    with main_file[0].file.storage().open() as pdf_file:
        content = pdf_file.read()

    # Extract data from pdf
    pdf_extractor = PDFExtractor()
    pdf_metadata = format_extracted_data(pdf_extractor.process_raw(content))

    return make_response(jsonify(pdf_metadata))
