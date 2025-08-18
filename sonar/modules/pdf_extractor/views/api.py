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

"""API Views."""

from __future__ import absolute_import, print_function

from flask import Blueprint, jsonify, request

from sonar.modules.pdf_extractor.pdf_extractor import PDFExtractor
from sonar.modules.pdf_extractor.utils import extract_text_from_content

api_blueprint = Blueprint(
    "pdf_extractor",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/pdf-extractor",
)


@api_blueprint.route("/metadata", methods=["POST"])
def metadata():
    """Extract PDF metadata and return as a json object."""
    try:
        if "file" not in request.files:
            raise Exception("File not found")

        # Get the file posted
        pdf_file = request.files["file"]

        pdf_extractor = PDFExtractor()

        # Extract metadata from PDF
        return jsonify(pdf_extractor.process_raw(pdf_file.read()))
    except Exception as exception:
        return jsonify(dict(error=str(exception))), 400


@api_blueprint.route("/full-text", methods=["POST"])
def full_text():
    """Extract PDF metadata and return as a json object."""
    try:
        if "file" not in request.files:
            raise Exception("File not found")

        # Get the file posted
        pdf_file = request.files["file"]

        # Extract full-text
        text = extract_text_from_content(pdf_file.read())

        return jsonify(text=text)
    except Exception as exception:
        return jsonify(dict(error=str(exception))), 400
