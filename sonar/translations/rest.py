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
from flask_babelex import get_domain

api_blueprint = Blueprint('translations', __name__)


@api_blueprint.route('/translations/<lang>.json')
def get_translations(lang):
    """Exposes translations in JSON format.

    :param lang: language ISO 639-1 Code (two chars).
    """
    domain = get_domain()

    path = next(p for p in domain.paths if p.find('sonar/translations') > -1)

    po_file_name = f'{path}/{lang}/LC_MESSAGES/{domain.domain}.po'

    if not os.path.isfile(po_file_name):
        abort(404)

    data = {}

    try:
        translations = polib.pofile(po_file_name)
    except Exception:
        current_app.logger.error(
            'unable to open po file: {po}'.format(po=po_file_name))
        abort(404)

    for entry in translations:
        data[entry.msgid] = entry.msgstr or entry.msgid

    return jsonify(data)
