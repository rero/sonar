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

"""Monitoring views."""

from functools import wraps

from flask import Blueprint, abort, jsonify, request
from flask_security import current_user
from invenio_search import current_search_client

from sonar.modules.documents.urn import Urn
from sonar.modules.permissions import superuser_access_permission
from sonar.monitoring.api.data_integrity import DataIntegrityMonitoring
from sonar.monitoring.api.database import DatabaseMonitoring

api_blueprint = Blueprint('monitoring_api', __name__, url_prefix='/monitoring')


def is_superuser(func):
    """Decorator checking if a user is logged and has role `superuser`."""

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401

        if not superuser_access_permission.can():
            return jsonify({'error': 'Forbidden'}), 403

        return func(*args, **kwargs)

    return decorated_view


@api_blueprint.before_request
@is_superuser
def check_for_superuser():
    """Check if user is superuser before each request, with decorator."""


@api_blueprint.route('/db/connections/count')
def db_connection_count():
    """Information about current database connections."""
    try:
        db_monitoring = DatabaseMonitoring()
        return jsonify({'data': db_monitoring.count_connections()})
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/db/activity')
def db_activity():
    """Current database activity."""
    try:
        db_monitoring = DatabaseMonitoring()
        return jsonify({'data': db_monitoring.activity()})
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/data/status')
def data_status():
    """Status of data integrity."""
    try:
        data_monitoring = DataIntegrityMonitoring()
        return jsonify({
            'data': {
                'status': 'green' if not data_monitoring.has_error() else 'red'
            }
        })
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/data/info')
def data_info():
    """Info of data integrity."""
    try:
        data_monitoring = DataIntegrityMonitoring()
        return jsonify({
            'data':
            data_monitoring.info(with_detail=('detail' in request.args))
        })
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/es')
def elastic_search():
    """Displays elastic search cluster info.

    :return: jsonified elastic search cluster info.
    """
    try:
        info = current_search_client.cluster.health()
        return jsonify({'data': info})
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/urn')
def unregistered_urn():
    """Count of unregistered urn pids.

    :return: jsonified count information.
    """
    try:
        days = int(args.get('days', 0)) if (args := request.args) else 0
        info = Urn.get_urn_pids(days=days)
        return jsonify({'data': info})
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500
