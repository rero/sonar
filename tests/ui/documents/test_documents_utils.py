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

"""Test documents utils."""

from sonar.modules.documents import utils


def test_publication_statement_text():
    """Test publication statement text."""
    # With statement
    assert utils.publication_statement_text({
        'type':
        'bf:Publication',
        'startDate':
        '1990',
        'statement': [{
            "label": [{
                "value": "Lausanne"
            }],
            "type": "bf:Place"
        }, {
            "label": [{
                "value": "Bulletin officiel du Directoire"
            }],
            "type": "bf:Agent"
        }, {
            "label": [{
                "value": "1798-1799"
            }],
            "type": "Date"
        }]
    }) == {
        'default': 'Lausanne : Bulletin officiel du Directoire, 1798-1799'
    }

    # Without statement
    assert utils.publication_statement_text({
        'type': 'bf:Publication',
        'startDate': '1990'
    }) == '1990'
