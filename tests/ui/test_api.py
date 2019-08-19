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

"""Test SONAR api."""

from flask import url_for
from invenio_app.factory import create_api
from invenio_indexer import current_record_to_index
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from sonar.modules.documents.api import DocumentRecord

create_app = create_api


def test_create(app):
    """Test creating a record."""
    DocumentRecord.create({
        "pid": "1",
        "title": "The title of the record"
    })

    DocumentRecord.create({
        "pid": "2",
        "title": "The title of the record"
    }, dbcommit=True)


def test_get_ref_link(app):
    """Test ref link."""
    assert DocumentRecord.get_ref_link('document', '1') == 'https://sonar.ch' \
        '/api/document/1'


def test_get_record_by_pid(app):
    """Test get record by PID."""
    assert DocumentRecord.get_record_by_pid('ABCD') is None

    record = DocumentRecord.create({
        "pid": "ABCD",
        "title": "The title of the record"
    })

    assert DocumentRecord.get_record_by_pid('ABCD')['pid'] == 'ABCD'

    record.delete()

    assert DocumentRecord.get_record_by_pid('ABCD') is None


def test_dbcommit(app):
    """Test record commit to db."""
    record = DocumentRecord.create({
        "title": "The title of the record"
    })

    record.dbcommit()
    assert DocumentRecord.get_record_by_pid(
        '1')['title'] == 'The title of the record'


def test_reindex(app, db, client):
    """Test record reindex."""
    record = DocumentRecord.create({
        "pid": "100",
        "title": "The title of the record"
    })
    db.session.commit()

    indexer = RecordIndexer()
    indexer.index(record)

    index_name, doc_type = current_record_to_index(record)
    current_search.flush_and_refresh(index_name)

    headers = [('Content-Type', 'application/json')]

    url = url_for('invenio_records_rest.doc_item', pid_value='100')

    response = client.get(url, headers=headers)
    data = response.json

    assert response.status_code == 200
    assert data['metadata']['title'] == 'The title of the record'
