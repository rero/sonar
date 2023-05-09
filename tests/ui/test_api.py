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

"""Test SONAR api."""

from copy import deepcopy

import mock
import pytest
from flask import url_for
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api
from invenio_pidstore.models import PersistentIdentifier, Redirect
from six import BytesIO

from sonar.modules.api import SonarRecord
from sonar.modules.documents.api import DocumentIndexer, DocumentRecord

create_app = create_api


def test_index_record(client, db, document_json, superuser):
    """Test index a record."""
    login_user_via_session(client, email=superuser['email'])

    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    total = res.json['hits']['total']['value']
    record = DocumentRecord.create(deepcopy(document_json), commit=True)

    indexer = DocumentIndexer()
    indexer.index(record)

    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == (total + 1)


def test_remove_from_index(client, db, document, superuser):
    """Test remove a record from index."""
    login_user_via_session(client, email=superuser['email'])

    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    total = res.json['hits']['total']['value']

    indexer = DocumentIndexer()
    indexer.delete(document)

    res = client.get(url_for('invenio_records_rest.doc_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == (total - 1)


def test_get_record_class_by_pid_type(app):
    """Test get record class by PID type."""
    record = SonarRecord.get_record_class_by_pid_type('doc')
    assert record.__name__ == 'DocumentRecord'


def test_get_all_pids(document):
    """Test get all identifiers for a record type."""
    result = list(DocumentRecord.get_all_pids())
    assert result == ['1']

    # with delete --> false
    document.delete()
    result = list(DocumentRecord.get_all_pids())
    assert result == []

    # with delete --> true
    result = list(DocumentRecord.get_all_pids(with_deleted=True))
    assert result == ['1']


def test_create(document_json):
    """Test creating a record."""
    record = DocumentRecord.create(deepcopy(document_json))
    assert DocumentRecord.get_record_by_pid(
        record['pid'])['pid'] == record['pid']
    DocumentRecord.create(deepcopy(document_json), dbcommit=True)
    assert DocumentRecord.get_record_by_pid(
        record['pid'])['pid'] == record['pid']


def test_get_ref_link():
    """Test ref link."""
    assert DocumentRecord.get_ref_link('document', '1') == 'https://sonar.ch' \
        '/api/document/1'


def test_get_record_by_pid(app, document_json):
    """Test get record by PID."""
    assert DocumentRecord.get_record_by_pid('not-existing') is None

    record = DocumentRecord.create(deepcopy(document_json))

    assert DocumentRecord.get_record_by_pid(
        record['pid'])['pid'] == record['pid']

    record.delete()

    assert DocumentRecord.get_record_by_pid(record['pid']) is None


def test_dbcommit(app, document_json):
    """Test record commit to db."""
    record = DocumentRecord.create(deepcopy(document_json))
    record.dbcommit()

    assert DocumentRecord.get_record_by_pid(
        record['pid'])['pid'] == record['pid']
    record.delete()


def test_reindex(client, document_json, superuser):
    """Test record reindex."""
    record = DocumentRecord.create(deepcopy(document_json), commit=True)

    indexer = DocumentIndexer()
    indexer.index(record)

    headers = [('Content-Type', 'application/json')]

    url = url_for('invenio_records_rest.doc_item', pid_value=record['pid'])

    login_user_via_session(client, email=superuser['email'])

    response = client.get(url, headers=headers)
    data = response.json

    assert response.status_code == 200
    assert data['metadata']['pid'] == record['pid']
    record.delete(delindex=True)


def test_get_pid_by_ref_link(document):
    """Test resolving PID by the given reference link."""
    with pytest.raises(Exception) as e:
        SonarRecord.get_pid_by_ref_link('falsy-link')
    assert str(e.value) == 'falsy-link is not a valid ref link'

    link = url_for('invenio_records_rest.doc_item',
                   _external=True,
                   pid_value='10000')

    pid = SonarRecord.get_pid_by_ref_link(link)
    assert pid == '10000'


def test_get_record_by_ref_link(document):
    """Test getting a record by a reference link."""
    link = url_for('invenio_records_rest.doc_item',
                   _external=True,
                   pid_value=document['pid'])

    record = DocumentRecord.get_record_by_ref_link(link)
    assert record['pid'] == document['pid']


def test_add_file_from_url(document):
    """Test add file to document by giving its URL."""
    # OK
    document.add_file_from_url(
        'https://doc.rero.ch/record/328028/files/nor_irc.pdf', 'test.pdf')
    assert len(document.files) == 3
    assert document.files['test.pdf']['label'] == 'test.pdf'

    # Non existing file URL
    document.add_file_from_url(
        'https://doc.rero.ch/pdf-url', 'test2.pdf')
    assert len(document.files) == 4
    assert document.files['test2.pdf']['label'] == 'test2.pdf'


@mock.patch('sonar.modules.documents.api.extract_text_from_content')
def test_add_file(mock_extract, app, pdf_file, document):
    """Test add file to document."""
    with open(pdf_file, 'rb') as file:
        content = file.read()

    mock_extract.return_value = 'Fulltext content'

    # Successful file add
    document.add_file(content, 'test1.pdf')
    assert document.files['test1.pdf']
    assert document.files['test1-pdf.txt']

    # Test already existing files
    document.add_file(content, 'test1.pdf')
    assert len(document.files) == 3

    # Importing files is disabled
    app.config['SONAR_DOCUMENTS_IMPORT_FILES'] = False
    document.add_file(content, 'test3.pdf')
    assert 'test3.pdf' not in document.files

    # Extracting fulltext is disabled
    app.config['SONAR_DOCUMENTS_IMPORT_FILES'] = True
    app.config['SONAR_DOCUMENTS_EXTRACT_FULLTEXT_ON_IMPORT'] = False
    document.add_file(content, 'test4.pdf')
    assert document.files['test4.pdf']
    assert 'test4-pdf.txt' not in document.files

    # Test exception when extracting fulltext
    app.config['SONAR_DOCUMENTS_EXTRACT_FULLTEXT_ON_IMPORT'] = True

    def exception_side_effect(data):
        raise Exception("Fulltext extraction error")

    mock_extract.side_effect = exception_side_effect
    document.add_file(content, 'test5.pdf')
    assert document.files['test5.pdf']
    assert 'test5-pdf.txt' not in document.files


def test_get_main_file(document_with_file):
    """Test getting the main file of a record."""
    # Test getting file with order 1
    assert document_with_file.get_main_file().key == 'test1.pdf'

    # Test if file have order 1 but not right type
    document_with_file.files['test1.pdf']['type'] = 'fake'
    assert not document_with_file.get_main_file()

    # Test if no files have order 1
    document_with_file.files['test1.pdf']['order'] = 2
    document_with_file.files['test1.pdf']['type'] = 'file'
    assert document_with_file.get_main_file().key == 'test1.pdf'

    for file in document_with_file.files:
        file.remove()

    assert not document_with_file.get_main_file()


def test_create_thumbnail(document, pdf_file):
    """Test create a thumbnail for document's file."""
    with open(pdf_file, 'rb') as file:
        content = file.read()

    document.files['test.pdf'] = BytesIO(content)

    # Successful thumbail creation
    document.create_thumbnail(document.files['test.pdf'])
    assert len(document.files) == 2
    assert document.files['test-pdf.jpg']

    document.files['test.pdf'].remove()
    document.files['test-pdf.jpg'].remove()

    # Failed creation of thumbnail
    document.files['test.txt'] = BytesIO(b'Hello, World')
    document.create_thumbnail(document.files['test.txt'])
    assert len(document.files) == 1


def test_get_record_by_bucket(app, db, document_with_file):
    """Test retrieving a record with a given bucket."""
    # OK
    record = SonarRecord.get_record_by_bucket(document_with_file['_bucket'])
    assert record

    # Record bucket not found
    assert not SonarRecord.get_record_by_bucket(
        '9bca9173-2c7b-4e22-bd6d-46e4f972dbf89')

    # Not record class found
    app.config.get('RECORDS_REST_ENDPOINTS',
                   {}).get('doc', {}).pop('record_class', None)
    assert not SonarRecord.get_record_by_bucket(document_with_file['_bucket'])
    app.config['RECORDS_REST_ENDPOINTS']['doc'][
        'record_class'] = DocumentRecord

    # Persistent identifier not found
    Redirect.query.delete()
    pid = PersistentIdentifier.get('doc', document_with_file['pid'])
    db.session.delete(pid)
    db.session.commit()
    pid = PersistentIdentifier.get('oai',
                                   'oai:sonar.ch:' + document_with_file['pid'])
    db.session.delete(pid)
    db.session.commit()
    assert not SonarRecord.get_record_by_bucket(document_with_file['_bucket'])


def test_sync_files(document_with_file):
    """Test update files for record."""
    document_with_file.sync_files(document_with_file.files['test1.pdf'])
    assert len(document_with_file.files) == 3
