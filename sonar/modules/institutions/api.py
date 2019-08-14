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

"""Institution Api."""


from functools import partial

from ..api import SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
InstitutionProvider = type(
    'InstitutionProvider',
    (Provider,),
    dict(pid_type='inst')
)
# minter
institution_pid_minter = partial(id_minter, provider=InstitutionProvider)
# fetcher
institution_pid_fetcher = partial(id_fetcher, provider=InstitutionProvider)


class InstitutionSearch(SonarSearch):
    """Search institutions."""

    class Meta:
        """Search only on item index."""

        index = 'institutions'
        doc_types = []


class InstitutionRecord(SonarRecord):
    """Institution record class."""

    minter = institution_pid_minter
    fetcher = institution_pid_fetcher
    provider = InstitutionProvider
    schema = 'institution'
