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

"""Test affiliations resolver."""

from sonar.affiliations import AffiliationResolver


def test_affiliations_property():
    """Test loading affiliations from file."""
    affiliation_resolver = AffiliationResolver()
    assert len(affiliation_resolver.affiliations) == 78


def test_resolve():
    """Test resolve affiliations."""
    affiliation_resolver = AffiliationResolver()

    assert not affiliation_resolver.resolve(None)

    test_string = "Institute for Computer Music and Sound Technology, Zurich University of the Arts, Switzerland"
    assert affiliation_resolver.resolve(test_string) == ["ZHdK (Zurich)"]

    test_string = "IST"
    assert affiliation_resolver.resolve(test_string) == ["IST"]

    test_string = (
        "Clinic for Cardiovascular Surgery, University HospitalZurich, Raemistrasse 100, 8091 Zurich, Switzerland"
    )
    assert affiliation_resolver.resolve(test_string) == ["University of Zurich and Hospital"]

    test_string = (
        "Institute for Research in Biomedicine (IRB), "
        "Faculty of Biomedical Sciences, USI, "
        "Switzerland - Graduate School for Cellular and Biomedical Sciences, "
        "University of Bern, 3012 Bern, Switzerland"
    )
    assert affiliation_resolver.resolve(test_string) == [
        "University of Bern and Hospital",
        "Università della Svizzera italiana",
    ]

    test_string = (
        "Centre for Research in Environmental Epidemiology (CREAL), Barcelona "
        "08003, Spain; CIBER Epidemiología y Salud Pública (CIBERESP), "
        "Barcelona 08003, Spain; Universitat Pompeu Fabra (UPF), Barcelona "
        "08003, Spain; Hospital del Mar Medical Research Institute (IMIM), "
        "Barcelona 08003, Spain."
    )
    assert not affiliation_resolver.resolve(test_string)

    test_string = "Not existing"
    assert not affiliation_resolver.resolve(test_string)

    test_string = "University of Freiburg"
    assert not affiliation_resolver.resolve(test_string)
