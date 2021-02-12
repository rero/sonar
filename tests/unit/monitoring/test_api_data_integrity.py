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

"""Test data integrity monitoring."""

import pytest
from invenio_search import current_search

from sonar.modules.documents.api import DocumentRecord
from sonar.monitoring.api.data_integrity import DataIntegrityMonitoring


def test_db_count(app, es_clear, document):
    """Test DB count."""
    monitoring = DataIntegrityMonitoring()

    # Resource not configured
    with pytest.raises(Exception) as exception:
        monitoring.get_db_count('not-existing')
    assert str(exception.value) == 'No endpoint configured for "not-existing"'

    # OK
    assert monitoring.get_db_count('doc') == 1

    # With deleted
    document.delete()
    assert monitoring.get_db_count('doc') == 0
    assert monitoring.get_db_count('doc', True) == 1


def test_es_count(app, es_clear, document):
    """Test ES count."""
    monitoring = DataIntegrityMonitoring()

    # Resource not configured
    with pytest.raises(Exception) as exception:
        monitoring.get_es_count('not-existing')
    assert str(exception.value) == 'No index found for "not-existing"'

    # OK
    assert monitoring.get_es_count('documents') == 1


def test_missing_pids(app, es_clear, document_json):
    """Test missing PIDs."""
    document_json['pid'] = '1000'

    document = DocumentRecord.create(data=document_json, dbcommit=True)
    monitoring = DataIntegrityMonitoring()

    # Only in DB
    assert monitoring.missing_pids('doc') == {
        'db': ['1000'],
        'es': [],
        'es_double': []
    }

    # OK
    document.reindex()
    assert monitoring.missing_pids('doc') == {
        'db': [],
        'es': [],
        'es_double': []
    }

    # Only in ES
    document.delete()
    assert monitoring.missing_pids('doc') == {
        'db': [],
        'es': ['1000'],
        'es_double': []
    }

    # With deleted
    assert monitoring.missing_pids('doc', True) == {
        'db': [],
        'es': [],
        'es_double': []
    }

    # Duplicate
    document2 = DocumentRecord.create(data=document_json, dbcommit=True)
    document2.reindex()
    current_search.flush_and_refresh('documents')
    assert monitoring.missing_pids('doc') == {
        'db': [],
        'es': ['1000'],
        'es_double': ['1000']
    }

    # Index not configured
    app.config.get('RECORDS_REST_ENDPOINTS')['doc'].pop('search_index', None)
    with pytest.raises(Exception) as exception:
        monitoring.missing_pids('doc')
    assert str(
        exception.value) == 'No "search_index" configured for resource "doc"'
    app.config.get(
        'RECORDS_REST_ENDPOINTS')['doc']['search_index'] = 'documents'


def test_info(app, es_clear, document, deposit):
    """Test info."""
    monitoring = DataIntegrityMonitoring()
    info = monitoring.info()
    for doc_type in ['depo', 'doc', 'org', 'proj', 'user']:
        assert doc_type in info


def test_has_error(app, es_clear, document):
    """Test if data has error."""
    # No error
    monitoring = DataIntegrityMonitoring()
    assert not monitoring.hasError()

    # Error
    document.delete()
    assert monitoring.hasError()
