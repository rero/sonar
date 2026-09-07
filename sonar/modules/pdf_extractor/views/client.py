# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""API Views."""

from flask import Blueprint, render_template

from sonar.modules.permissions import is_user_logged_and_submitter

blueprint = Blueprint(
    "pdf",
    __name__,
    static_folder="../static",
    template_folder="../templates",
    url_prefix="/pdf-extractor",
)


@blueprint.route("/test", methods=["GET"])
@is_user_logged_and_submitter
def test():
    """Test upload file and extracting metadata."""
    return render_template("test.html")
