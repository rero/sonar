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
    assert record['pid'] == '10000'

    # Record not found
    record = DocumentRecord.get_record_by_identifier([{
        'value': 'oai:unknown',
        'type': 'bf:Identifier'
    }])
    assert not record


def test_get_affiliations():
    """Test getting controlled affiliations."""
    affiliation = '''
    Institute for Research in Biomedicine (IRB), Faculty of Biomedical
    Sciences, Università della Svizzera italiana, Switzerland - Graduate
    School for Cellular and Biomedical Sciences, University of Bern, c/o
    Theodor Kocher Institute, Freiestrasse 1, P.O. Box 938, CH-3000 Bern 9,
    Switzerland
    '''
    affiliations = DocumentRecord.get_affiliations(affiliation)
    assert affiliations == [
        'Uni of Bern and Hospital', 'Uni of Italian Switzerland'
    ]

    affiliations = DocumentRecord.get_affiliations(None)
    assert not affiliations


def test_load_affiliations():
    """Test load affiliations from file."""
    DocumentRecord.load_affiliations()
    assert len(DocumentRecord.affiliations) == 77
