# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Sitemap views."""

import os

from flask import Blueprint, Response, abort, current_app

blueprint = Blueprint("sitemap", __name__, template_folder="templates", url_prefix="/")


@blueprint.route("/<org_code:view>/sitemap.xml")
def sitemap(view):
    """Get the sitemap file."""
    file_path = ["sitemap.xml"]
    if view != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
        file_path.insert(0, view)
    return response_file(file_path)


@blueprint.route("/<org_code:view>/sitemap_<int:index>.xml")
def sitemap_index(view, index):
    """Get the sitemap index file."""
    file_path = [f"sitemap_{index}.xml"]
    if view != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
        file_path.insert(0, view)
    return response_file(file_path)


def response_file(file_path):
    """Generate the file path and load file."""

    def stream_file(sitemap_file):
        """Stream file."""
        with open(sitemap_file, encoding="utf-8", buffering=100000) as f:
            yield from f

    sitemap_folder = current_app.config.get("SONAR_APP_SITEMAP_FOLDER_PATH")
    sitemap_file = os.path.join(sitemap_folder, *file_path)
    if not os.path.exists(sitemap_file):
        abort(404)
    return Response(stream_file(sitemap_file), mimetype="application/xml")
