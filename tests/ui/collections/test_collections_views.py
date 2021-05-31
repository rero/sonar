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

"""Test collections views."""

from flask import url_for


def test_index(app, db, client, document, organisation, collection):
    """Test list of collections."""
    # No collection index for global view
    assert client.get(url_for('collections.index',
                              view='global')).status_code == 404

    # OK in organisation context but no collection listed because there's no
    # document linked.
    result = client.get(url_for('collections.index', view='org'))
    assert result.status_code == 200
    assert b'No collection found' in result.data

    # OK in organisation context and the collection has a document linked.
    document['collections'] = [{
        '$ref':
        'https://sonar.ch/api/collections/{pid}'.format(pid=collection['pid'])
    }]
    document.commit()
    db.session.commit()
    document.reindex()
    result = client.get(url_for('collections.index', view='org'))
    assert result.status_code == 200
    assert b'<h3>Collection name</h3>' in result.data


def test_detail(app, client, organisation, collection):
    """Test collection detail."""
    # No detail view in global context
    assert client.get(
        url_for('invenio_records_ui.coll',
                view='global',
                pid_value=collection['pid'])).status_code == 404

    # OK in organisation context
    result = client.get(
        url_for('invenio_records_ui.coll',
                view='org',
                pid_value=collection['pid']))
    assert result.status_code == 302
    assert result.location.find(f'collection_view={collection["pid"]}') != -1
