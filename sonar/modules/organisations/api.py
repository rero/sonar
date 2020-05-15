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

from werkzeug.local import LocalProxy

from sonar.modules.users.api import current_user_record
from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..providers import Provider
from .minters import id_minter

current_organisation = LocalProxy(lambda: OrganisationRecord.get_organisation_by_user(current_user_record))

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
    schema = 'organisations/organisation-v1.0.0.json'

    @classmethod
    def get_organisation_by_user(cls, user):
        if not user or not user.get('organisation'):
            return None

        return cls.get_record_by_ref_link(user['organisation']['$ref'])


class OrganisationIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = OrganisationRecord
