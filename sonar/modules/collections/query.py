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

"""Query."""

from elasticsearch_dsl import Q
from flask import current_app, request

from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import default_search_factory
from sonar.modules.users.api import current_user_record


def search_factory(self, search):
    """Search factory.

    :param Search search: Search instance
    :return: Tuple with search instance and URL arguments
    :rtype: tuple
    """
    search, urlkwargs = default_search_factory(self, search)

    if current_app.config.get('SONAR_APP_DISABLE_PERMISSION_CHECKS'):
        return (search, urlkwargs)

    # Cannot suggest a record which is the current collection or the current
    # collection is one of the parents.
    if '.suggest' in request.args.get('q',
                                      '') and request.args.get('currentPid'):
        search = search.query(
            Q('bool',
              must_not=[Q('match',
                          path='/' + request.args.get('currentPid'))]))

    # Records are not filtered for superusers.
    if current_user_record.is_superuser:
        return (search, urlkwargs)

    # For admins, records are filtered by organisation of the current user.
    search = search.filter('term',
                           organisation__pid=current_organisation['pid'])

    return (search, urlkwargs)
