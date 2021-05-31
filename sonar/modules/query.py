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

"""Query factories for REST API."""

from __future__ import absolute_import, print_function

from elasticsearch_dsl.query import Q
from flask import request


def get_operator_and_query_type(qstr=None):
    """Get a tuple with the operator and the query type.

    :param qstr: Query string.
    :returns: Tuple containing operator and query type.
    """
    if not qstr:
        return None

    # If qstr contains `:` keyword, operator is forced to `AND` and query type
    # `query_string`.
    if ':' in qstr:
        return ('AND', 'query_string')

    # Default to `AND`
    operator = request.args.get('operator', 'AND')

    if operator.upper() not in ['AND', 'OR']:
        raise Exception('Only "AND" or "OR" operators allowed')

    # With operator AND, with always use simple query string.
    query_type = 'simple_query_string' \
        if operator.upper() == 'AND' else 'query_string'

    return (operator, query_type)


def default_search_factory(self, search, query_parser=None):
    """Parse query using elasticsearch DSL query.

    :param search: Elastic search DSL search instance.
    :param query_parser: Custom query parser.
    :returns: Tuple with search instance and URL arguments.
    """

    def _default_parser(qstr=None):
        """Default parser that uses the Q() from elasticsearch_dsl.

        :param qstr: Query string.
        :returns: Query object.
        """
        if not qstr:
            return Q()

        operator, query_type = get_operator_and_query_type(qstr)

        return Q(query_type, query=qstr, default_operator=operator)

    from invenio_records_rest.facets import default_facets_factory
    from invenio_records_rest.sorter import default_sorter_factory

    query_string = request.values.get('q')

    # Use query parser given to function or the default one.
    query_parser = query_parser or _default_parser

    # Search query
    search = search.query(query_parser(query_string))

    # Get index corresponding to record type.
    search_index = getattr(search, '_original_index', search._index)[0]

    # Build facets
    search, urlkwargs = default_facets_factory(search, search_index)

    # Sort records
    search, sortkwargs = default_sorter_factory(search, search_index)
    for key, value in sortkwargs.items():
        urlkwargs.add(key, value)

    urlkwargs.add('q', query_string)

    # Add explanation to hits
    if request.args.get('debug'):
        search = search.extra(explain=True)

    return search, urlkwargs


def and_term_filter(field):
    """Create a term filter.

    :param field: Field name.
    :return: Function that returns a boolean AND query between term values.
    """
    def inner(values):
        must = []
        for value in values:
            must.append(Q('term', **{field: value}))
        return Q('bool', must=must)
    return inner


def missing_field_filter(field):
    """Filter to search data which does not contain the specified field.

    :param field: Property that must not exist.
    :returns: elasticsearch DSL query.
    """
    def inner(values):
        return Q('bool', must_not=[Q('exists', field=field)])
    return inner


def collection_filter(field):
    """Filter for collections."""
    def inner(values):
        must = []
        for value in values:
            must.append(
                Q('nested',
                  path='collections',
                  query=Q('bool', must=Q('term', **{field: value}))))
        return Q('bool', must=must)

    return inner
