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

"""Test subdivisions facets in documents."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, db, client, document, subdivision, superuser):
    document['subdivisions'] = [{
        '$ref':
        'https://sonar.ch/api/subdivisions/{pid}'.format(
            pid=subdivision['pid'])
    }]
    document.commit()
    db.session.commit()
    document.reindex()

    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.doc_list', view='org'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1
    assert res.json['aggregations']['subdivision']['buckets'] == [{
        'key':
        '2',
        'doc_count':
        1,
        'name':
        'Subdivision name'
    }]

    # Don't display aggregation in global context
    res = client.get(url_for('invenio_records_rest.doc_list', view='global'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1
    assert 'subdivision' not in res.json['aggregations']
