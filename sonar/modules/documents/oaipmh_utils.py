# -*- coding: utf-8 -*-
#
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

"""Invenio OAIPMH server utils."""

from invenio_oaiserver import current_oaiserver

from .dumpers import IndexerDumper


def getrecord_fetcher(record_uuid):
    """Fetch record data as dict for serialization."""
    record = current_oaiserver.record_cls.get_record(record_uuid)
    record_dict = record.dumps(IndexerDumper())
    record_dict["updated"] = record.updated
    return record_dict
