# Swiss Open Access Repository
# Copyright (C) 2025 RERO
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

"""User record extension to delete deposits."""

from invenio_records.extensions import RecordExtension


class DeleteDepositsExtension(RecordExtension):
    """Deletes associated deposits."""

    def post_delete(self, record, force=False):
        """Called after a record is deleted."""
        from sonar.modules.users.tasks import delete_deposits

        delete_deposits.delay(record["pid"], force=force, dbcommit=True, delindex=True)
