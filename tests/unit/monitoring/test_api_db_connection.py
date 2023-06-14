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

"""Test DB connections API."""

from invenio_db import db

from sonar.monitoring.api.database import DatabaseMonitoring


def test_count(app, monkeypatch):
    """Test count connections."""
    db_monitoring = DatabaseMonitoring()

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
    assert db_monitoring.count_connections() == {
        'max': 100,
        'used': 10,
        'reserved_for_super': 2,
        'free': 88
    }


def test_activity(app, monkeypatch):
    """Test activity."""
    db_monitoring = DatabaseMonitoring()

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
    assert db_monitoring.activity() == [{
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
