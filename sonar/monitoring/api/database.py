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

"""DB monitoring."""

from invenio_db import db
from sqlalchemy import text


class DatabaseMonitoring:
    """DB monitoring."""

    def count_connections(self):
        """Count current DB connections.

        :returns: Dict with information about current connections.
        """
        query = text(
            """
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
        )
        max_conn, used, res_for_super, free = db.session.execute(query).first()
        return {
            "max": max_conn,
            "used": used,
            "reserved_for_super": res_for_super,
            "free": free,
        }

    def activity(self):
        """Get current activity.

        :returns: A list of the current activities.
        """
        query = text(
            """
                SELECT
                    pid, application_name, client_addr, client_port, backend_start,
                    xact_start, query_start,  wait_event, state, left(query, 64)
                FROM
                    pg_stat_activity
                ORDER BY query_start DESC
            """
        )
        results = db.session.execute(query).fetchall()
        return {
            pid: {
                "application_name": application_name,
                "client_addr": client_addr,
                "client_port": client_port,
                "backend_start": backend_start,
                "xact_start": xact_start,
                "query_start": query_start,
                "wait_event": wait_event,
                "state": state,
                "left": left,
            }
            for pid, application_name, client_addr, client_port, backend_start, xact_start, query_start, wait_event, state, left in results
        }
