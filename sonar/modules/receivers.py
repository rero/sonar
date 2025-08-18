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

"""Listeners for application."""

from sonar.modules.api import SonarRecord


def file_uploaded_listener(sender, obj):
    """Function executed when a file is uploaded.

    :param obj: Object version.
    """
    try:
        sync_record_files(obj, False)
    except Exception:
        pass


def file_deleted_listener(sender, obj):
    """Function executed when a file is deleted.

    :param obj: Object version.
    """
    try:
        sync_record_files(obj, True)
    except Exception:
        pass


def sync_record_files(file, deleted=False):
    """Sync files in record corresponding to bucket.

    :param file: File object
    :param delete: Wether file is deleted or not.
    """
    record = SonarRecord.get_record_by_bucket(file.bucket_id)

    if not record:
        return

    record.sync_files(file, deleted)
