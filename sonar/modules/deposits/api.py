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

    minter = deposit_pid_minter
    fetcher = deposit_pid_fetcher
    provider = DepositProvider
    schema = 'deposit'

    @classmethod
    def create(cls,
               data,
               id_=None,
               dbcommit=False,
               with_bucket=True,
               **kwargs):
        """Create deposit record."""
        record = super(DepositRecord, cls).create(data,
                                                  id_=id_,
                                                  dbcommit=dbcommit,
                                                  with_bucket=with_bucket,
                                                  **kwargs)
        return record
