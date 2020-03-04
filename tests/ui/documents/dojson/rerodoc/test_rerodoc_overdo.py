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

"""Test RERODOC overdo."""

import pytest

from sonar.modules.documents.dojson.rerodoc.overdo import Overdo
from sonar.modules.institutions.api import InstitutionRecord


def test_get_affiliations():
    """Test getting controlled affiliations."""
    affiliation = '''
    Institute for Research in Biomedicine (IRB), Faculty of Biomedical
    Sciences, Università della Svizzera italiana, Switzerland - Graduate
    School for Cellular and Biomedical Sciences, University of Bern, c/o
    Theodor Kocher Institute, Freiestrasse 1, P.O. Box 938, CH-3000 Bern 9,
    Switzerland
    '''
    overdo = Overdo()
    affiliations = overdo.get_affiliations(affiliation)
    assert affiliations == [
        'Uni of Bern and Hospital', 'Uni of Italian Switzerland'
    ]

    affiliations = overdo.get_affiliations(None)
    assert not affiliations


def test_load_affiliations():
    """Test load affiliations from file."""
    Overdo.load_affiliations()
    assert len(Overdo.affiliations) == 77


def test_create_institution(app):
    """Test create institution."""
    Overdo.create_institution('test')

    # Institution creation OK
    institution = InstitutionRecord.get_record_by_pid('test')
    assert institution
    assert institution['pid'] == 'test'

    # No institution key provided
    with pytest.raises(Exception) as exception:
        Overdo.create_institution(None)
    assert str(exception.value) == 'No key provided'


def test_extract_date():
    """Test date extraction."""
    # No date provided
    assert Overdo.extract_date(None) == (None, None)

    # Full first date
    assert Overdo.extract_date('1980-01-01') == ('1980-01-01', None)

    # Full first date, variant
    assert Overdo.extract_date('01-01-1980') == ('01-01-1980', None)

    # First year only
    assert Overdo.extract_date('1980') == ('1980', None)

    # First year only, variant with dash
    assert Overdo.extract_date('1980-') == ('1980', None)

    # Start and end year
    assert Overdo.extract_date('1980-2010') == ('1980', '2010')

    # Error on date format
    with pytest.raises(Exception) as exception:
        assert Overdo.extract_date('AAAA')
    assert str(exception.value) == 'Date "AAAA" is not recognized'


def test_get_contributor_role():
    """Test contributor role mapping."""
    overdo = Overdo()
    overdo.blob_record = {}

    # dgs
    assert overdo.get_contributor_role('Dir.') == 'dgs'

    # prt
    assert overdo.get_contributor_role('Libr./Impr.') == 'prt'

    # joint author
    assert overdo.get_contributor_role('joint author') == 'cre'

    # with role but no mapping found
    assert not overdo.get_contributor_role('not-mapped')

    # no role, no doc type
    assert not overdo.get_contributor_role(None)

    # no role, doc type mapped to 'cre'
    overdo.blob_record = {'980__': {'a': 'PREPRINT'}}
    assert overdo.get_contributor_role(None) == 'cre'

    # no role, doc type mapped to 'ctb'
    overdo.blob_record = {'980__': {'a': 'BOOK'}}
    assert overdo.get_contributor_role(None) == 'ctb'


def test_verify(app):
    """Test verify result."""
    overdo = Overdo()
    overdo.blob_record = {}

    # No provision activity and no type
    overdo.verify({})
    assert not overdo.result_ok

    # No provision activity and type make it mandatory
    overdo.verify({'documentType': 'coar:c_816b'})
    assert not overdo.result_ok

    # Provision activity is present in result
    overdo.blob_record = {}
    overdo.verify({'provisionActivity': {}})
    assert overdo.result_ok

    # No provision activity and provision activity is optional
    overdo.verify({'documentType': 'coar:c_beb9'})
    assert overdo.result_ok
