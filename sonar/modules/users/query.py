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

"""Query for users."""

from elasticsearch_dsl.query import Q
from flask import current_app

from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import default_search_factory
from sonar.modules.users.api import current_user_record


def search_factory(self, search, query_parser=None):
    """User search factory.

    :param search: Search instance.
    :param query_parser: Url arguments.
    :returns: Tuple with search instance and URL arguments.
    """
    search, urlkwargs = default_search_factory(self, search)

    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return (search, urlkwargs)

    # Searching for existing email, everybody can do that
    if urlkwargs.get('q') and urlkwargs['q'].startswith('email:'):
        search = search.source(includes=['pid'])
        return (search, urlkwargs)

    # Super users can list all records
    if current_user_record.is_superuser:
        return (search, urlkwargs)

    # For admins, records are filtererd by user's organisation and they cannot
    # get superuser records.
    if current_user_record.is_admin:
        first_filter = Q('term', organisation__pid=current_organisation['pid'])
        second_filter = Q('bool',
                          must_not={'exists': {
                              'field': 'organisation'
                          }})
        search = search \
            .filter('bool', filter=first_filter | second_filter) \
            .filter('bool', must_not={'term': {'role': 'superuser'}})
        return (search, urlkwargs)

    # For remaining roles, they can only list themselves
    search = search.filter('term', pid=current_user_record['pid'])

    return (search, urlkwargs)
