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

"""Document Api."""

from functools import partial

from ..api import SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
DocumentProvider = type('DocumentProvider', (Provider, ), dict(pid_type='doc'))
# minter
document_pid_minter = partial(id_minter, provider=DocumentProvider)
# fetcher
document_pid_fetcher = partial(id_fetcher, provider=DocumentProvider)


class DocumentSearch(SonarSearch):
    """Search documents."""

    class Meta:
        """Search only on item index."""

        index = 'documents'
        doc_types = []


class DocumentRecord(SonarRecord):
    """Document record class."""

    minter = document_pid_minter
    fetcher = document_pid_fetcher
    provider = DocumentProvider
    schema = 'document'

    @classmethod
    def get_record_by_identifier(cls, identifiers):
        """Get a record by its identifier.

        :param list identifiers: List of identifiers
        """
        for identifier in identifiers:
            if identifier['type'] == 'bf:Identifier':
                results = list(DocumentSearch().filter(
                    'term', identifiedBy__value=identifier['value']).source(
                        includes=['pid']))

                if results:
                    return cls.get_record_by_pid(results[0]['pid'])

        return None
