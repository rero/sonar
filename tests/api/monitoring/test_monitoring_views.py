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

"""Test monitoring views."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db


def test_db_connection_count(client, es_clear, monkeypatch, admin, superuser):
    """Test DB connections count."""
    # Not logged
    response = client.get(url_for('monitoring_api.db_connection_count'))
    assert response.status_code == 401

    login_user_via_session(client, email=admin['email'])

    # Wrong role
    response = client.get(url_for('monitoring_api.db_connection_count'))
    assert response.status_code == 403

    login_user_via_session(client, email=superuser['email'])

    # Error
    response = client.get(url_for('monitoring_api.db_connection_count'))
    assert response.status_code == 500

    class MockConnectionQuery():
        """Mock connection query."""

        def first(self):
            """Simulate returning the first result."""
            return {
                'max_conn': 100,
                'used': 10,
                'res_for_super': 2,
                'free': 88
            }

    monkeypatch.setattr(db.session,
                        'execute', lambda *args: MockConnectionQuery())

    # OK
    response = client.get(url_for('monitoring_api.db_connection_count'))
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'max': 100,
            'used': 10,
            'reserved_for_super': 2,
            'free': 88
        }
    }


def test_db_activity(client, es_clear, monkeypatch, admin, superuser):
    """Test DB activity."""
    login_user_via_session(client, email=superuser['email'])

    # Error
    response = client.get(url_for('monitoring_api.db_activity'))
    assert response.status_code == 500

    class MockActivityQuery():
        """Mock activity query."""

        def fetchall(self):
            """Simulate returning the results."""
            return [{
                'application_name': '',
                'backend_start': 'Mon, 08 Feb 2021 10:46:55 GMT',
                'client_addr': '10.233.92.25',
                'client_port': 33382,
                'left':
                '\n        SELECT\n            pid, application_name, client',
                'query_start': 'Mon, 08 Feb 2021 10:46:55 GMT',
                'state': 'active',
                'wait_event': None,
                'xact_start': 'Mon, 08 Feb 2021 10:46:55 GMT'
            }]

    monkeypatch.setattr(db.session,
                        'execute', lambda *args: MockActivityQuery())

    # Error
    response = client.get(url_for('monitoring_api.db_activity'))
    assert response.status_code == 200
    assert response.json == {
        'data': [{
            'application_name': '',
            'client_address': '10.233.92.25',
            'client_port': 33382,
            'query':
            '\n        SELECT\n            pid, application_name, client',
            'query_start': 'Mon, 08 Feb 2021 10:46:55 GMT',
            'state': 'active',
            'transaction_start': 'Mon, 08 Feb 2021 10:46:55 GMT',
            'wait_event': None
        }]
    }


def test_data_status(client, es_clear, organisation, superuser, document,
                     monkeypatch):
    """Test integrity status."""
    login_user_via_session(client, email=superuser['email'])

    # OK
    response = client.get(url_for('monitoring_api.data_status'))
    assert response.status_code == 200
    assert response.json == {'data': {'status': 'green'}}

    # Has error
    document.delete()
    response = client.get(url_for('monitoring_api.data_status'))
    assert response.status_code == 200
    assert response.json == {'data': {'status': 'red'}}

    # Throw error
    def mock_info(*args):
        raise Exception('Unknown exception')

    monkeypatch.setattr(
        'sonar.monitoring.api.data_integrity.DataIntegrityMonitoring.info',
        mock_info)
    response = client.get(url_for('monitoring_api.data_status'))
    assert response.status_code == 500
    assert response.json == {'error': 'Unknown exception'}


def test_data_info(client, es_clear, superuser, document, monkeypatch):
    """Test integrity info."""
    login_user_via_session(client, email=superuser['email'])

    response = client.get(url_for('monitoring_api.data_info'))
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'depo': {
                'db': 0,
                'es': 0,
                'db-es': 0,
                'index': 'deposits'
            },
            'doc': {
                'db': 1,
                'es': 1,
                'db-es': 0,
                'index': 'documents'
            },
            'org': {
                'db': 1,
                'es': 1,
                'db-es': 0,
                'index': 'organisations'
            },
            'projects': {
                'db': 0,
                'es': 0,
                'db-es': 0,
                'index': 'projects'
            },
            'user': {
                'db': 1,
                'es': 1,
                'db-es': 0,
                'index': 'users'
            },
            'coll': {
                'db': 0,
                'es': 0,
                'db-es': 0,
                'index': 'collections'
            },
            'subd': {
                'db': 0,
                'es': 0,
                'db-es': 0,
                'index': 'subdivisions'
            }
        }
    }

    # With detail
    response = client.get(url_for('monitoring_api.data_info', detail=True))
    assert response.status_code == 200
    assert response.json['data']['doc']['detail'] == {
        'db': [],
        'es': [],
        'es_double': []
    }

    # Throw error
    def mock_info(*args, **kwargs):
        raise Exception('Unknown exception')

    monkeypatch.setattr(
        'sonar.monitoring.api.data_integrity.DataIntegrityMonitoring.info',
        mock_info)
    response = client.get(url_for('monitoring_api.data_info', detail=True))
    assert response.status_code == 500
    assert response.json == {'error': 'Unknown exception'}


def test_elastic_search(client, superuser, monkeypatch):
    """Test elastic search health."""
    login_user_via_session(client, email=superuser['email'])

    response = client.get(url_for('monitoring_api.elastic_search'))
    assert response.status_code == 200
    assert 'active_primary_shards' in response.json['data']
    assert 'status' in response.json['data']

    # Throw error
    def mock_info(*args):
        raise Exception('Unknown exception')

    monkeypatch.setattr('invenio_search.current_search_client.cluster.health',
                        mock_info)
    response = client.get(url_for('monitoring_api.elastic_search'))
    assert response.status_code == 500
    assert response.json == {'error': 'Unknown exception'}
