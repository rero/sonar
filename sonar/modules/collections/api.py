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

"""Record API."""

from functools import partial

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..providers import Provider
from .config import Configuration
from .minters import id_minter

# provider
RecordProvider = type('RecordProvider', (Provider, ),
                      dict(pid_type=Configuration.pid_type))
# minter
pid_minter = partial(id_minter, provider=RecordProvider)
# fetcher
pid_fetcher = partial(id_fetcher, provider=RecordProvider)


class Record(SonarRecord):
    """Record."""

    minter = pid_minter
    fetcher = pid_fetcher
    provider = RecordProvider
    schema = Configuration.schema

    @classmethod
    def create(cls, data, id_=None, dbcommit=False, with_bucket=True,
               **kwargs):
        """Create record.

        :param dict data: Metadata of the new record
        :param str id_: UUID to use if not generated
        :param bool dbcommit: Wether to commit into DB during creation
        :param bool with_bucket: Wether to create a bucket for record
        :return: New record instance
        :rtype: Record
        """
        return super().create(data,
                                         id_=id_,
                                         dbcommit=dbcommit,
                                         with_bucket=with_bucket,
                                         **kwargs)


class RecordSearch(SonarSearch):
    """Record search."""

    class Meta:
        """Search only on item index."""

        index = Configuration.index
        doc_types = []


class RecordIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = Record
