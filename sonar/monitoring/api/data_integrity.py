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

"""Data integrity monitoring."""

from elasticsearch.exceptions import NotFoundError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_search import RecordsSearch

from sonar.proxies import sonar


class DataIntegrityMonitoring:
    """Data integrity monitoring."""

    def get_db_count(self, rec_type, with_deleted=False):
        """Get database count.

        Get count of items in the database for the given document type.

        :param rec_type: Record type.
        :param with_deleted: Count also deleted items.
        :returns: Items count.
        """
        if service := sonar.service(rec_type):
            rec_type = service.record_cls.pid_type

        query = PersistentIdentifier.query.filter_by(pid_type=rec_type)
        if not with_deleted:
            query = query.filter_by(status=PIDStatus.REGISTERED)

        return query.count()

    def get_es_count(self, index):
        """Get elasticsearch count.

        Get count of items in elasticsearch for the given index.

        :param index: Elasticsearch index.
        :return: Items count.
        """
        try:
            return RecordsSearch(index=index).query().count()
        except NotFoundError:
            raise Exception(f'No index found for "{index}"')

    def missing_pids(self, rec_type, with_deleted=False):
        """Get ES and DB counts.

        :param rec_type: Record type.
        :param with_deleted: Check also delete items in database.
        """
        index = sonar.endpoints.get(rec_type, None)

        if not index:
            raise Exception(f'No index configured for resource "{rec_type}"')

        result = {"es": [], "es_double": [], "db": []}

        # Elastic search PIDs
        es_pids = {}
        for hit in RecordsSearch(index=index).source(["pid", "id"]).scan():
            pid_value = hit.pid
            # for resources pid is a dict
            if not isinstance(pid_value, str):
                pid_value = hit.id
            if es_pids.get(pid_value):
                result["es_double"].append(hit.pid)
            es_pids[pid_value] = 1

        # Database PIDs
        if service := sonar.service(rec_type):
            rec_type = service.record_cls.pid_type
        query = PersistentIdentifier.query.filter_by(pid_type=rec_type)
        if not with_deleted:
            query = query.filter_by(status=PIDStatus.REGISTERED)

        for identifier in query:
            if es_pids.get(identifier.pid_value):
                es_pids.pop(identifier.pid_value)
            else:
                result["db"].append(identifier.pid_value)

        # Transform dictionary to list
        result["es"] = [v for v in es_pids]

        return result

    def info(self, with_deleted=False, with_detail=False):
        """Get count details for all resources.

        :param with_deleted: Count also deleted items in database.
        :param with_detail: Show the detail of the differences.
        :returns: Dictionary with differences for each resource.
        """
        info = {}

        for rec_type, index in sonar.endpoints.items():
            es_count = self.get_es_count(index)
            db_count = self.get_db_count(rec_type)

            info[rec_type] = {
                "db": db_count,
                "es": es_count,
                "db-es": db_count - es_count,
                "index": index,
            }

            if with_detail:
                info[rec_type]["detail"] = self.missing_pids(rec_type, with_deleted)

        return info

    def has_error(self, with_deleted=False):
        """Check if any endpoint has an integrity error.

        :param with_deleted: Count also deleted items in database.
        :returns: True if an error is found
        """
        for rec_type, item in self.info(with_deleted).items():
            if item["db-es"] != 0:
                return True

        return False
