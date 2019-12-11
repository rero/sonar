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

"""Deposit API."""

from functools import partial

from ..api import SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
DepositProvider = type('DepositProvider', (Provider, ), dict(pid_type='depo'))
# minter
deposit_pid_minter = partial(id_minter, provider=DepositProvider)
# fetcher
deposit_pid_fetcher = partial(id_fetcher, provider=DepositProvider)


class DepositSearch(SonarSearch):
    """Search deposits."""

    class Meta:
        """Search only on item index."""

        index = 'deposits'
        doc_types = []


class DepositRecord(SonarRecord):
    """Deposit record class."""

    STEP_DIFFUSION = 'diffusion'

    STATUS_IN_PROGRESS = 'in progress'
    STATUS_VALIDATED = 'validated'
    STATUS_TO_VALIDATE = 'to validate'

    minter = deposit_pid_minter
    fetcher = deposit_pid_fetcher
    provider = DepositProvider
    schema = 'deposit'

    @classmethod
    def create(cls, data, id_=None, dbcommit=False, with_bucket=True,
               **kwargs):
        """Create deposit record."""
        record = super(DepositRecord, cls).create(data,
                                                  id_=id_,
                                                  dbcommit=dbcommit,
                                                  with_bucket=with_bucket,
                                                  **kwargs)
        return record

    def populate_with_pdf_metadata(self, pdf_metadata, default_title=None):
        """Update data for record."""
        self['metadata'] = {}

        if 'title' in pdf_metadata:
            self['metadata']['title'] = pdf_metadata['title']
        else:
            self['metadata']['title'] = default_title

        if 'languages' in pdf_metadata:
            self['metadata']['languages'] = pdf_metadata['languages']

        if 'authors' in pdf_metadata:
            if 'contributors' not in self:
                self['contributors'] = []

            for author in pdf_metadata['authors']:
                self['contributors'].append({'name': author['name']})

        if 'abstract' in pdf_metadata:
            if 'abstracts' not in self['metadata']:
                self['metadata']['abstracts'] = []

            self['metadata']['abstracts'].append(pdf_metadata['abstract'])

        if 'journal' in pdf_metadata:
            self['metadata']['journal'] = pdf_metadata['journal']

        return self
