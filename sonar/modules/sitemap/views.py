# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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
        with open(sitemap_file, "r", encoding="utf-8", buffering=100000) as f:
            yield from f

    sitemap_folder = current_app.config.get("SONAR_APP_SITEMAP_FOLDER_PATH")
    sitemap_file = os.path.join(sitemap_folder, *file_path)
    if not os.path.exists(sitemap_file):
        abort(404)
    return Response(stream_file(sitemap_file), mimetype="application/xml")
