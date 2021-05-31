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

"""Test collections facets in documents."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, db, client, document, collection, superuser):
    document['collections'] = [{
        '$ref':
        'https://sonar.ch/api/collections/{pid}'.format(pid=collection['pid'])
    }]
    document.commit()
    db.session.commit()
    document.reindex()

    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1
    assert res.json['aggregations']['collection']['buckets'] == [{
        'key':
        '2',
        'doc_count':
        1,
        'collection1': {
            'doc_count_error_upper_bound':
            0,
            'sum_other_doc_count':
            0,
            'buckets': [{
                'key': '3',
                'doc_count': 1,
                'collection2': {
                    'doc_count_error_upper_bound': 0,
                    'sum_other_doc_count': 0,
                    'buckets': []
                },
                'name': 'Collection name'
            }]
        },
        'name':
        'Parent collection'
    }]

    # Test with collection filter
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.doc_list', collection='2'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1

    # Test with sub collection filter
    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.doc_list', collection1='3'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1
