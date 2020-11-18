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

"""Test affiliations resolver."""

from sonar.affiliations import AffiliationResolver


def test_affiliations_property():
    """Test loading affiliations from file."""
    affiliation_resolver = AffiliationResolver()
    assert len(affiliation_resolver.affiliations) == 77


def test_resolve():
    """Test resolve affiliations."""
    affiliation_resolver = AffiliationResolver()

    assert not affiliation_resolver.resolve(None)

    test_string = ('Institute for Computer Music and Sound Technology, Zurich'
                   ' University of the Arts, Switzerland')
    assert affiliation_resolver.resolve(test_string) == 'ZHdK (Zurich)'

    test_string = 'IST'
    assert affiliation_resolver.resolve(test_string) == 'IST'

    test_string = ('Clinic for Cardiovascular Surgery, University Hospital'
                   'Zurich, Raemistrasse 100, 8091 Zurich, Switzerland')
    assert affiliation_resolver.resolve(
        test_string) == 'Uni of Zurich and Hospital'

    test_string = 'Not existing'
    assert not affiliation_resolver.resolve(test_string)
