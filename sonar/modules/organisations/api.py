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

"""Organisation Api."""


from functools import partial

from ..api import SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
OrganisationProvider = type(
    'OrganisationProvider',
    (Provider,),
    dict(pid_type='org')
)
# minter
organisation_pid_minter = partial(id_minter, provider=OrganisationProvider)
# fetcher
organisation_pid_fetcher = partial(id_fetcher, provider=OrganisationProvider)


class OrganisationSearch(SonarSearch):
    """Search organisations."""

    class Meta:
        """Search only on item index."""

        index = 'organisations'
        doc_types = []


class OrganisationRecord(SonarRecord):
    """Organisation record class."""

    minter = organisation_pid_minter
    fetcher = organisation_pid_fetcher
    provider = OrganisationProvider
    schema = 'organisation'
