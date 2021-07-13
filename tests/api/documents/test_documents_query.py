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

"""Test documents query."""

from flask import url_for


def test_collection_query(db, client, document, collection, es_clear):
    document['collections'] = [{
        '$ref':
        'https://sonar.ch/api/collections/{pid}'.format(pid=collection['pid'])
    }]
    document.commit()
    db.session.commit()
    document.reindex()

    res = client.get(
        url_for('invenio_records_rest.doc_list',
                view='org',
                collection_view=collection['pid']))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1
    assert not res.json['aggregations'].get('collection')


def test_masked_document(db, client, document, es_clear):
    """Test masked document."""
    # Not masked (property not exists)
    res = client.get(url_for('invenio_records_rest.doc_list', view='global'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1

    # Not masked
    document['masked'] = False
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for('invenio_records_rest.doc_list', view='global'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1

    # Masked
    document['masked'] = True
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for('invenio_records_rest.doc_list', view='global'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 0
