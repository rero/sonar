# -*- coding: utf-8 -*-
#
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

"""Rest endpoints for translations."""

import os

import polib
from flask import Blueprint, abort, current_app, jsonify

api_blueprint = Blueprint('translations', __name__)




@api_blueprint.route('/translations/<lang>.json')
def get_translations(lang):
    """Exposes translations in JSON format.

    :param lang: language ISO 639-1 Code (two chars).
    """
    babel = current_app.extensions['babel']
    paths = babel.default_directories
    try:
        path = next(p for p in paths if p.find('sonar/translations') > -1)
    except StopIteration:
        current_app.logger.error(f'translations for {lang} does not exist')
        abort(404)

    po_file_name = f'{path}/{lang}/LC_MESSAGES/{babel.default_domain}.po'
    if not os.path.isfile(po_file_name):
        abort(404)
    try:
        po = polib.pofile(po_file_name)
    except Exception:
        current_app.logger.error(f'unable to open po file: {po_file_name}')
        abort(404)
    data = {entry.msgid: entry.msgstr or entry.msgid for entry in po}
    return jsonify(data)
