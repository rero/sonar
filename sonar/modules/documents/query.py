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

"""Query for documents."""

from invenio_records_rest.query import es_search_factory

from flask import current_app, request

from sonar.modules.organisations.api import current_organisation
from sonar.modules.users.api import current_user_record


def search_factory(self, search, query_parser=None):
    """Documents search factory."""
    view = request.args.get('view')

    search, urlkwargs = es_search_factory(self, search)

    if view:
        if view != current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION'):
            search = search.filter('term', organisation__pid=view)
    else:
        if current_user_record and not current_user_record.is_super_admin and \
            current_organisation:
            search = search.filter(
                'term', organisation__pid=current_organisation['pid'])

    return (search, urlkwargs)
