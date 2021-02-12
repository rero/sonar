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

"""Test RERODOC overdo."""

import pytest

from sonar.modules.documents.dojson.rerodoc.overdo import Overdo
from sonar.modules.organisations.api import OrganisationRecord


def test_create_organisation(app, bucket_location, without_oaiset_signals):
    """Test create organisation."""
    Overdo.create_organisation('test')

    # Organisation creation OK
    organisation = OrganisationRecord.get_record_by_pid('test')
    assert organisation
    assert organisation['pid'] == 'test'

    # No organisation key provided
    with pytest.raises(Exception) as exception:
        Overdo.create_organisation(None)
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
