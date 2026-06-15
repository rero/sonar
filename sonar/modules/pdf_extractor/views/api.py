# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""API Views."""

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
        return jsonify({"error": str(exception)}), 400


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
        return jsonify({"error": str(exception)}), 400
