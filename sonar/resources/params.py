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

"""Results filtering based on request params."""

from invenio_records_resources.services.records.params.base import \
    ParamInterpreter


class FilterParams(ParamInterpreter):
    """Search filters."""

    def apply(self, identity, search, params):
        """Apply filters.

        :param identity: Identity representing the logged user.
        :param search: Elasticsearch object.
        :param params: Additional params.
        :returns: Elasticsearch object.
        """
        filters = self.config.search_facets_options.get('filters', {})
        facets_args = params.get('facets', {})

        for k in set(facets_args.keys()) & set(filters.keys()):
            values = facets_args[k]
            search = search.filter(filters[k](values))

        return search
