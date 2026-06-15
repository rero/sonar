# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Rest endpoints for translations."""

import os

import polib
from flask import Blueprint, abort, current_app, jsonify

api_blueprint = Blueprint("translations", __name__)


@api_blueprint.route("/translations/<lang>.json")
def get_translations(lang):
    """Exposes translations in JSON format.

    :param lang: language ISO 639-1 Code (two chars).
    """
    babel = current_app.extensions["babel"]
    paths = babel.default_directories
    try:
        path = next(p for p in paths if p.find("sonar/translations") > -1)
    except StopIteration:
        current_app.logger.error(f"translations for {lang} does not exist")
        abort(404)

    po_file_name = f"{path}/{lang}/LC_MESSAGES/{babel.default_domain}.po"
    if not os.path.isfile(po_file_name):
        abort(404)
    try:
        po = polib.pofile(po_file_name)
    except Exception:
        current_app.logger.error(f"unable to open po file: {po_file_name}")
        abort(404)
    data = {entry.msgid: entry.msgstr or entry.msgid for entry in po}
    return jsonify(data)
