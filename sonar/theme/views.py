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

import re

from flask import Blueprint, abort, current_app, jsonify, render_template, \
    request
from flask_login import current_user
from invenio_jsonschemas import current_jsonschemas
from invenio_jsonschemas.errors import JSONSchemaNotFound

from sonar.modules.babel_extractors import translate
from sonar.modules.deposits.permissions import DepositPermission
from sonar.modules.documents.permissions import DocumentPermission
from sonar.modules.organisations.permissions import OrganisationPermission
from sonar.modules.permissions import can_access_manage_view
from sonar.modules.users.api import UserRecord, current_user_record
from sonar.modules.users.permissions import UserPermission

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
        data['metadata']['is_superuser'] = user.is_superuser
        data['metadata']['is_admin'] = user.is_admin
        data['metadata']['is_moderator'] = user.is_moderator
        data['metadata']['is_publisher'] = user.is_publisher
        data['metadata']['is_user'] = user.is_user
        data['metadata']['permissions'] = {
            'users': {
                'add': UserPermission.create(user),
                'list': UserPermission.list(user)
            },
            'documents': {
                'add': DocumentPermission.create(user),
                'list': DocumentPermission.list(user)
            },
            'organisations': {
                'add': OrganisationPermission.create(user),
                'list': OrganisationPermission.list(user)
            },
            'deposits': {
                'add': DepositPermission.create(user),
                'list': DepositPermission.list(user)
            }
        }

    # TODO: If an organisation is associated to user and only when running
    # tests, organisation cannot not be encoded to JSON after call of
    # user.replace_refs() --> check why
    return jsonify(data)


@blueprint.route('/schemas/<record_type>')
def schemas(record_type):
    """Return schema for the editor.

    :param record_type: Type of resource.
    :returns: JSONified schema or a 404 if not found.
    """
    rec_type = record_type
    rec_type = re.sub('ies$', 'y', rec_type)
    rec_type = re.sub('s$', '', rec_type)

    try:
        current_jsonschemas.get_schema.cache_clear()
        schema_name = '{}/{}-v1.0.0.json'.format(record_type, rec_type)
        schema = current_jsonschemas.get_schema(schema_name)

        # TODO: Maybe find a proper way to do this.
        if record_type in [
                'users', 'documents'
        ] and not current_user.is_anonymous and current_user_record:
            if record_type == 'users':
                # If user is admin, restrict available roles list.
                if current_user_record.is_admin:
                    schema['properties']['roles']['items'][
                        'enum'] = current_user_record.\
                            get_all_reachable_roles()
                # User cannot select role
                else:
                    schema['properties'].pop('roles')
                    if schema.get('propertiesOrder'):
                        schema['propertiesOrder'].remove('roles')

            if not current_user_record.is_superuser:
                schema['properties'].pop('organisation')
                if schema.get('propertiesOrder'):
                    schema['propertiesOrder'].remove('organisation')

        return jsonify({'schema': prepare_schema(schema)})
    except JSONSchemaNotFound:
        abort(404)


def prepare_schema(schema):
    """Prepare schema before sending it."""
    # Recursively translate properties in schema
    translate(schema,
              keys=current_app.config['SONAR_APP_BABEL_TRANSLATE_JSON_KEYS'])

    # Recursively hierarchize form option if a level property is available.
    def hierarchize_form_options(schema):
        """Hierarchize form options."""
        if schema.get('properties'):
            for key, value in schema['properties'].items():
                if value.get('form', {}).get('options'):
                    for option in value['form']['options']:
                        if option.get('level'):
                            option['label'] = "{spaces} {label}".format(
                                spaces='-' * 2 * option['level'],
                                label=option['label'])

                if value.get('type') == 'array' and value['items'][
                        'type'] == 'object':
                    hierarchize_form_options(value['items'])

                if value.get('type') == 'object':
                    hierarchize_form_options(value)

        for of_field in ['oneOf', 'anyOf', 'allOf', 'not']:
            if schema.get(of_field):
                for field in schema[of_field]:
                    hierarchize_form_options(field)

    hierarchize_form_options(schema)

    return schema
