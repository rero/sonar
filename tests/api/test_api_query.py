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

"""Test elasticsearch query string."""

import pytest
from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_api_query(client, document_with_file, document_json, make_document,
                   superuser):
    """Test simple flow using REST API."""
    headers = [('Content-Type', 'application/json')]
    login_user_via_session(client, email=superuser['email'])

    # get records without query string
    response = client.get(url_for('invenio_records_rest.doc_list'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1

    # with explanation
    response = client.get(url_for('invenio_records_rest.doc_list', debug=1),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1
    assert 'explanation' in response.json['hits']['hits'][0]

    # query string = 'title'
    response = client.get(url_for('invenio_records_rest.doc_list', q='title'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1

    # query string = 'titlé', record found with word "Title"
    response = client.get(url_for('invenio_records_rest.doc_list', q='titlé'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1

    # query string = 'resume', record found with word "Résumé"
    response = client.get(url_for('invenio_records_rest.doc_list', q='resume'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1

    # Multiple words in query string = 'resume title' and operator AND
    response = client.get(url_for('invenio_records_rest.doc_list',
                                  q='resume title',
                                  operator='AND'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1

    # Multiple words in query string = 'resume title' and operator AND, but
    # one word not found
    response = client.get(url_for('invenio_records_rest.doc_list',
                                  q='resume fake',
                                  operator='AND'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 0

    # Multiple words in query string = 'resume title' and operator OR
    response = client.get(url_for('invenio_records_rest.doc_list',
                                  q='resume title',
                                  operator='OR'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1

    # Multiple words in query string = 'resume title' and operator OR and one
    # word not found
    response = client.get(url_for('invenio_records_rest.doc_list',
                                  q='resume fake',
                                  operator='OR'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1

    # Test search in fulltext
    response = client.get(url_for('invenio_records_rest.doc_list',
                                  q='fulltext:the',
                                  debug=1),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1
    assert response.json['hits']['hits'][0]['explanation']['details']

    # Not allowed operator
    with pytest.raises(Exception) as exception:
        response = client.get(url_for('invenio_records_rest.doc_list',
                                      q='title',
                                      operator='not-allowed'),
                              headers=headers)
    assert str(exception.value) == 'Only "AND" or "OR" operators allowed'

    # Error during parsing of query string
    response = client.get(url_for('invenio_records_rest.doc_list',
                                  q='i/o',
                                  operator='OR'),
                          headers=headers)
    assert response.status_code == 400
    assert ('The syntax of the search query is invalid.' in response.get_data(
        as_text=True))

    # Test facets with AND operator.
    # Create a new document with only one subject
    document_json['subjects'] = [{
        'label': {
            'language': 'eng',
            'value': ['GARCH models']
        },
        'source': 'RERO'
    }]
    make_document('org')
    response = client.get(url_for(
        'invenio_records_rest.doc_list',
        subject=['Time series models', 'GARCH models']),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1
