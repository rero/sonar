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

import pytest

from sonar.modules.documents.api import DocumentRecord


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
