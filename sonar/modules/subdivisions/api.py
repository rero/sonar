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
    def get_pid_by_hash_key(cls, hash_key):
        """Get a record by a hash key.

        :param str hash_key: Hash key to find.
        :returns: The record found.
        :rtype: SonarRecord.
        """
        result = RecordSearch().filter(
            'term', hashKey=hash_key).source(includes='pid').scan()
        try:
            return next(result).pid
        except StopIteration:
            return None


class RecordSearch(SonarSearch):
    """Record search."""

    class Meta:
        """Search only on item index."""

        index = Configuration.index
        doc_types = []


class RecordIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = Record
