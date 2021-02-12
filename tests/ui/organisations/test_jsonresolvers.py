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

"""Test organisations jsonresolvers."""


def test_organisation_resolver(document):
    """Test organisation resolver."""
    assert document['organisation'][0].get('$ref')
    assert document['organisation'][0][
        '$ref'] == 'https://sonar.ch/api/organisations/org'

    assert document.replace_refs().get(
        'organisation')[0]['name'] == 'org'
