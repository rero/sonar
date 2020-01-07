# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Blueprint used for loading templates.

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""

from __future__ import absolute_import, print_function

from flask import Blueprint, jsonify, redirect, render_template, request, \
    url_for
from flask_login import current_user

from sonar.modules.permissions import can_access_manage_view
from sonar.modules.users.api import UserRecord

blueprint = Blueprint('sonar',
                      __name__,
                      template_folder='templates',
                      static_folder='static')


@blueprint.route('/error')
def error():
    """Error to generate exception for test purposes."""
    raise Exception('this is an error for test purposes')


@blueprint.route('/manage/')
@blueprint.route('/manage/<path:path>')
@can_access_manage_view
def manage(path=None):
    """Admin access page integrating angular ui."""
    if not path:
        return redirect(url_for('sonar.manage', path='records/documents'))

    return render_template('sonar/manage.html')


@blueprint.route('/logged-user/', methods=['GET'])
def logged_user():
    """Current logged user informations in JSON."""
    if current_user.is_anonymous:
        return jsonify({})

    user = UserRecord.get_user_by_current_user(current_user)

    if user and 'resolve' in request.args:
        user = user.replace_refs()

    data = {}

    if user:
        data['metadata'] = user.dumps()
        data['metadata']['is_super_admin'] = user.is_super_admin
        data['metadata']['is_admin'] = user.is_admin
        data['metadata']['is_moderator'] = user.is_moderator
        data['metadata']['is_user'] = user.is_user

    # TODO: If an organization is associated to user and only when running
    # tests, institution cannot not be encoded to JSON after call of
    # user.replace_refs() --> check why
    return jsonify(data)
