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

"""DB monitoring."""

from invenio_db import db


class DatabaseMonitoring():
    """DB monitoring."""

    def count_connections(self):
        """Count current DB connections.

        :returns: Dict with information about current connections.
        """
        query = """
            select
                max_conn, used, res_for_super,
                max_conn-used-res_for_super free
            from
                (
                    select count(*) used
                    from pg_stat_activity
                ) t1,
                (
                    select setting::int res_for_super
                    from pg_settings
                    where name=$$superuser_reserved_connections$$
                ) t2,
                (
                    select setting::int max_conn
                    from pg_settings
                    where name=$$max_connections$$
                ) t3
        """
        result = db.session.execute(query).first()

        return {
            'max': result['max_conn'],
            'used': result['used'],
            'reserved_for_super': result['res_for_super'],
            'free': result['free']
        }

    def activity(self):
        """Get current activity.

        :returns: A list of the current activities.
        """
        query = """
            SELECT
                pid, application_name, client_addr, client_port, backend_start,
                xact_start, query_start,  wait_event, state, left(query, 64)
            FROM
                pg_stat_activity
            ORDER BY query_start DESC
        """

        def format_row(row):
            """Format returned row from DB."""
            return {
                'application_name': row['application_name'],
                'client_address': row['client_addr'],
                'client_port': row['client_port'],
                'query': row['left'],
                'query_start': row['query_start'],
                'state': row['state'],
                'wait_event': row['wait_event'],
                'transaction_start': row['xact_start']
            }

        return list(map(format_row, db.session.execute(query).fetchall()))
