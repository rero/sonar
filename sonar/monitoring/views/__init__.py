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

from flask import Blueprint, current_app, jsonify, request
from flask_security import current_user
from invenio_pidstore.models import PIDStatus
from invenio_search import current_search_client
from redis import Redis

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


@api_blueprint.route('/db_connection_counts')
def db_connection_count():
    """Information about current database connections."""
    try:
        db_monitoring = DatabaseMonitoring()
        return jsonify({'data': db_monitoring.count_connections()})
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('db_connections')
def db_activity():
    """Current database activity."""
    try:
        db_monitoring = DatabaseMonitoring()
        return jsonify({'data': db_monitoring.activity()})
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/es_db_status')
def data_status():
    """Status of data integrity."""
    try:
        data_monitoring = DataIntegrityMonitoring()
        return jsonify({
            'data': {
                'status': 'red' if data_monitoring.has_error() else 'green'
            }
        })
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/es_db_counts')
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


@api_blueprint.route('/redis')
def redis():
    """Displays redis info.

    :return: jsonified redis info.
    """
    url = current_app.config.get('ACCOUNTS_SESSION_REDIS_URL',
                                 'redis://localhost:6379')
    redis = Redis.from_url(url)
    info = redis.info()
    return jsonify({'data': info})

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
def urn():
    """Count of unregistered urn pids.

    :return: jsonified count information.
    """
    data = dict()
    try:
        days = int(args.get('days', 0)) if (args := request.args) else 0
        count, pids = Urn.get_urn_pids(days=days)
        data['reserved'] = dict(count=count, pids=list(pids))
        count, pids = Urn.get_urn_pids(days=days, status=PIDStatus.REGISTERED)
        data['registered'] = dict(count=count)
        return jsonify(dict(data=data))
    except Exception as exception:
        return jsonify({'error': str(exception)}), 500


@api_blueprint.route('/es_indices')
def elastic_search_indices():
    """Displays Elasticsearch indices info.

    :return: jsonified Elasticsearch indices info.
    """
    info = current_search_client.cat.indices(
        bytes='b', format='json', s='index')
    info = {data['index']: data for data in info}
    return jsonify({'data': info})
