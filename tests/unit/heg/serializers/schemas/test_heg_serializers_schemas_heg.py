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

"""Test HEG schema."""

from sonar.heg.serializers.schemas.heg import HEGSchema


def test_heg_schema(app):
    """Test HEG schema."""
    data = {'_id': '111', 'language': 'en'}
    assert HEGSchema().dump(data) == {
        'documentType': 'coar:c_6501',
        'identifiedBy': [{
            'type': 'bf:Doi',
            'value': '111'
        }],
        'language': [{
            'type': 'bf:Language',
            'value': 'eng'
        }]
    }

    # With spanish language
    data = {'_id': '111', 'language': 'es'}
    assert HEGSchema().dump(data) == {
        'documentType': 'coar:c_6501',
        'identifiedBy': [{
            'type': 'bf:Doi',
            'value': '111'
        }],
        'language': [{
            'type': 'bf:Language',
            'value': 'spa'
        }]
    }

    # Without language
    data = {'_id': '111'}
    assert HEGSchema().dump(data) == {
        'documentType': 'coar:c_6501',
        'identifiedBy': [{
            'type': 'bf:Doi',
            'value': '111'
        }],
        'language': [{
            'type': 'bf:Language',
            'value': 'eng'
        }]
    }

    # With files
    data = {'_id': '111', 'pdf': 'https://some.domain/some.pdf'}
    assert HEGSchema().dump(data) == {
        'documentType': 'coar:c_6501',
        'identifiedBy': [{
            'type': 'bf:Doi',
            'value': '111'
        }],
        'language': [{
            'type': 'bf:Language',
            'value': 'eng'
        }]
    }
