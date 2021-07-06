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

"""Organisation Api."""

from functools import partial

from flask import _request_ctx_stack, has_request_context
from invenio_db import db
from invenio_oaiserver.models import OAISet
from werkzeug.local import LocalProxy

from sonar.modules.users.api import current_user_record

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..providers import Provider
from .minters import id_minter


def get_current_organisation():
    """Return current organisation from context."""
    if has_request_context() and not hasattr(_request_ctx_stack.top,
                                             'organisation_record'):
        ctx = _request_ctx_stack.top
        ctx.organisation_record = None if (
            not current_user_record or
            not current_user_record.get('organisation')
        ) else OrganisationRecord.get_record_by_ref_link(
            current_user_record['organisation']['$ref'])

    return getattr(_request_ctx_stack.top, 'organisation_record', None)


current_organisation = LocalProxy(get_current_organisation)

# provider
OrganisationProvider = type('OrganisationProvider', (Provider, ),
                            dict(pid_type='org'))
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

    def get_shared_or_dedicated_list(self):
        """Get the list of dedicated or shared organisations.

        :returns: Iterator of dedicated or shared organisations.
        """
        return self.filter('bool',
                           should=[{
                               'term': {
                                   'isDedicated': True
                               }
                           }, {
                               'term': {
                                   'isShared': True
                               }
                           }]).source(
                               ['pid', 'name', 'isShared',
                                'isDedicated']).execute().hits


class OrganisationRecord(SonarRecord):
    """Organisation record class."""

    minter = organisation_pid_minter
    fetcher = organisation_pid_fetcher
    provider = OrganisationProvider
    schema = 'organisations/organisation-v1.0.0.json'

    @classmethod
    def create(cls, data, id_=None, dbcommit=False, with_bucket=True,
               **kwargs):
        """Create organisation record."""
        # Create OAI set
        oaiset = OAISet(spec=data['code'], name=data['name'])
        db.session.add(oaiset)

        return super(OrganisationRecord, cls).create(data,
                                                     id_=id_,
                                                     dbcommit=dbcommit,
                                                     with_bucket=with_bucket,
                                                     **kwargs)

    @classmethod
    def get_or_create(cls, code, name=None):
        """Get or create an organisation.

        :param code: Organisation's code, equivalent to PID.
        :param name: Organisation's name.
        :returns: Organisations object.
        """
        organisation = cls.get_record_by_pid(code)

        if organisation:
            return organisation

        organisation = cls.create(
            {
                'code': code,
                'name': name if name else code
            }, dbcommit=True)
        organisation.reindex()
        return organisation

    def update(self, data):
        """Update data for record."""
        # Update OAI set name according to organisation's name
        oaiset = OAISet.query.filter(OAISet.spec == data['code']).first()

        if oaiset:
            oaiset.name = data['name']
            db.session.commit()

        super(OrganisationRecord, self).update(data)
        return self


class OrganisationIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = OrganisationRecord
