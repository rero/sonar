# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2024 RERO
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

"""Test DnbUrnService API."""


import requests_mock

from sonar.modules.documents.dnb import DnbUrnService


def test_dnb_sucessor(app):
    """Test a successor assignment."""
    with requests_mock.mock() as response:
        response.patch(requests_mock.ANY, status_code=204)
        DnbUrnService().set_successor(
            'urn:nbn:ch:rero-002-old', 'urn:nbn:ch:rero-002-new')
