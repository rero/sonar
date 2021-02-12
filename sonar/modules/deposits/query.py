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

"""Query for deposits."""

from flask import current_app

from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import default_search_factory
from sonar.modules.users.api import current_user_record


def search_factory(self, search, query_parser=None):
    """Deposit search factory.

    :param search: Search instance.
    :param query_parser: Url arguments.
    :returns: Tuple with search instance and URL arguments.
    """
    search, urlkwargs = default_search_factory(self, search)

    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return (search, urlkwargs)

    # For superusers, records are not filtered.
    if current_user_record.is_superuser:
        return (search, urlkwargs)

    # For admin and moderator, only records that belongs to his organisation.
    if current_user_record.is_admin or current_user_record.is_moderator:
        search = search.filter(
            'term', user__organisation__pid=current_organisation['pid'])
        return (search, urlkwargs)

    # For user, only records that belongs to him.
    if current_user_record.is_submitter:
        search = search.filter(
            'term', user__pid=current_user_record['pid'])

    return (search, urlkwargs)
