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

"""Monitoring views."""

from functools import wraps

from flask import Blueprint, abort, jsonify
from flask_security import current_user

from sonar.modules.permissions import superuser_access_permission
from sonar.monitoring.api.data_integrity import DataIntegrityMonitoring
from sonar.monitoring.api.database import DatabaseMonitoring

blueprint = Blueprint('monitoring_api', __name__, url_prefix='/monitoring')


def is_superuser(func):
    """Decorator checking if a user is logged and has role `superuser`."""

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(), 401

        if not superuser_access_permission.can():
            return jsonify({'status': 'error: Forbidden'}), 403

        return func(*args, **kwargs)

    return decorated_view


@blueprint.route('/db/connections/count')
@is_superuser
def db_connection_count():
    """Information about current database connections."""
    try:
        db_monitoring = DatabaseMonitoring()
        return jsonify(db_monitoring.count_connections())
    except Exception:
        abort(500)


@blueprint.route('/db/activity')
@is_superuser
def db_activity():
    """Current database activity."""
    try:
        db_monitoring = DatabaseMonitoring()
        return jsonify(db_monitoring.activity())
    except Exception:
        abort(500)


@blueprint.route('/data/status')
def data_status():
    """Status of data integrity."""
    data_monitoring = DataIntegrityMonitoring()
    return jsonify(
        {'status': 'green' if not data_monitoring.hasError() else 'red'})


@blueprint.route('/data/info')
@is_superuser
def data_info():
    """Info of data integrity."""
    data_monitoring = DataIntegrityMonitoring()
    return jsonify(data_monitoring.info())
