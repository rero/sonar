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

"""DocumentRecord Extensions."""

from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.extensions import RecordExtension

from ..ark.api import current_ark


class ArkDocumentExtension(RecordExtension):
    """Register/unregister Ark identifiers."""

    def post_create(self, record):
        """Called after a record is created.

        :param record: the invenio record instance to be processed.
        """
        self._create_or_update_ark(record)

    def pre_commit(self, record):
        """Called before a record is committed.

        :param record: the invenio record instance to be processed.
        """
        self._create_or_update_ark(record)

    def post_delete(self, record, force=False):
        """Called after a record is deleted.

        :param record: the invenio record instance to be processed.
        :param force: unused.
        """
        if record.get('ark'):
            response = current_ark.delete(record.get('pid'))
            ark_id = response.replace('success: ', '')
            p = PersistentIdentifier.get('ark', ark_id)
            p.delete()

    def _create_or_update_ark(self, record):
        """Create or update the ARK identifier.

        :param record: the invenio record instance to be processed.
        """
        if record.get('ark'):
            org = record.replace_refs().get('organisation', [{}])[0]
            pid = record.get('pid')
            ark_id = current_ark.create(
                pid,
                current_ark.target_url(pid, org.get('code', 'global')))
            p = PersistentIdentifier.get('ark', ark_id)
            if p.status == PIDStatus.RESERVED:
                p.register()

