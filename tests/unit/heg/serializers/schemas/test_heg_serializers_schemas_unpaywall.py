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

"""Test Unpaywall schema."""

from sonar.heg.serializers.schemas.unpaywall import UnpaywallSchema


def test_unpaywall_schema(app):
    """Test Unpaysqll schema."""
    data = {
        '_id': '111',
        'oa_status': 'green',
        'best_oa_location': {
            'url_for_pdf': 'https://pdf.url'
        }
    }
    assert UnpaywallSchema().dump(data) == {
        'oa_status':
        'green',
        'files': [{
            'key': 'fulltext.pdf',
            'label': 'Full-text',
            'order': 0,
            'type': 'file',
            'url': 'https://pdf.url'
        }]
    }

    # Without images
    data = {'_id': '111', 'oa_status': 'green'}
    assert UnpaywallSchema().dump(data) == {'oa_status': 'green', 'files': []}
