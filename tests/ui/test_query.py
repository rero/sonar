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

"""Test elasticsearch query."""

import pytest
from elasticsearch_dsl import Search
from invenio_search import current_search_client

from sonar.modules.query import and_term_filter, get_operator_and_query_type


def test_get_operator_and_query_type(app):
    """Test getting the operator and query_type for elasticsarch query."""
    # No query string
    assert not get_operator_and_query_type('')

    # Query string with `:`
    assert get_operator_and_query_type('pid:1') == ('AND', 'query_string')

    with app.test_request_context() as req:
        # Not allowed operator
        req.request.args = {'operator': 'not-allowed'}
        with pytest.raises(Exception) as exception:
            get_operator_and_query_type('test')
        assert str(exception.value) == 'Only "AND" or "OR" operators allowed'

        # With OR
        req.request.args = {'operator': 'OR'}
        assert get_operator_and_query_type('test') == ('OR', 'query_string')

        # With AND
        req.request.args = {'operator': 'AND'}
        assert get_operator_and_query_type('test') == ('AND',
                                                       'simple_query_string')


def test_open_access_filter(app, document, embargo_date):
    """Test open access filter."""
    # No filter
    search = Search(index='documents', using=current_search_client)
    assert len(search.execute()) == 1

    # No files associated with document --> not open access.
    search = search.query(and_term_filter('isOpenAccess')([True]))
    assert not search.execute()

    # Files with document, no access property --> open access.
    document.add_file(b'Test', 'test1.pdf')
    document.commit()
    document.reindex()
    search = search.query(and_term_filter('isOpenAccess')([True]))
    assert len(search.execute()) == 1

    # Files with document, access property is closed --> not open access.
    document.files['test1.pdf']['access'] = 'coar:c_16ec'
    document.commit()
    document.reindex()
    search = search.query(and_term_filter('isOpenAccess')([True]))
    assert not search.execute()

    # Files with document, access property is open access --> open access.
    document.files['test1.pdf']['access'] = 'coar:c_abf2'
    document.commit()
    document.reindex()
    search = search.query(and_term_filter('isOpenAccess')([True]))
    assert len(search.execute()) == 1

    # Files with document, access property is embargo access and no date
    # provided --> not open access.
    document.files['test1.pdf']['access'] = 'coar:c_f1cf'
    document.commit()
    document.reindex()
    search = search.query(and_term_filter('isOpenAccess')([True]))
    assert not search.execute()

    # Files with document, access property is embargo access and date is in the
    # future --> not open access.
    document.files['test1.pdf']['access'] = 'coar:c_f1cf'
    document.files['test1.pdf']['embargo_date'] = embargo_date.isoformat()
    document.commit()
    document.reindex()
    search = search.query(and_term_filter('isOpenAccess')([True]))
    assert not search.execute()

    # Files with document, access property is embargo access and date is in the
    # past --> open access.
    document.files['test1.pdf']['access'] = 'coar:c_f1cf'
    document.files['test1.pdf']['embargo_date'] = '2021-01-01'
    document.commit()
    document.reindex()
    search = search.query(and_term_filter('isOpenAccess')([True]))
    assert len(search.execute()) == 1
