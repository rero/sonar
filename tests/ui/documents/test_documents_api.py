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

"""Test documents API."""

from sonar.modules.documents.api import DocumentRecord


def test_get_record_by_identifier(app, document):
    """Test getting record by its identifier."""
    # Record found
    record = DocumentRecord.get_record_by_identifier([{
        'value': '111111',
        'type': 'bf:Local'
    }])
    assert record['pid'] == document['pid']

    # Record not found
    record = DocumentRecord.get_record_by_identifier([{
        'value': 'oai:unknown',
        'type': 'bf:Identifier'
    }])
    assert not record


def test_get_next_file_order(document_with_file, document):
    """Test getting next file position."""
    # One file with order 1
    assert document_with_file.get_next_file_order() == 2

    # Adding a new file
    document_with_file.add_file(b'File content', 'file2.pdf')
    assert document_with_file.get_next_file_order() == 3

    # No order properties
    for file in document_with_file.files:
        document_with_file.files[file.key].data.pop('order', None)
    assert document_with_file.get_next_file_order() == 2

    # No files
    assert document.get_next_file_order() == 1


def test_get_files_list(document, pdf_file):
    """Test getting the list of files, filtered and orderd."""
    document.add_file(b'file 1', 'test1.pdf', order=2)
    document.add_file(b'file 2', 'test2.pdf', order=1)
    document.add_file(b'file 3', 'test3.pdf', order=3)
    document.add_file(b'file 4', 'test4.pdf', order=4, type="not-file")
    files = document.get_files_list()
    assert len(files) == 3
    assert files[0]['order'] == 1


def test_get_documents_by_project(db, project, document):
    """"Test getting documents by a project."""
    document['projects'] = [{'$ref': 'https://sonar.ch/api/projects/11111'}]
    document.commit()
    document.reindex()
    db.session.commit()

    documents = DocumentRecord.get_documents_by_project(project['pid'])
    assert documents[0]['pid'] == '1'
    assert documents[0]['permalink'] == 'http://localhost/global/documents/1'
