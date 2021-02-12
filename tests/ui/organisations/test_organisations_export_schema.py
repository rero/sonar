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

"""Test Marshmallow export schema."""

from io import BytesIO

from sonar.modules.organisations.serializers.schemas.export import \
    ExportSchemaV1


def test_export_schema(organisation):
    """Test export schema."""
    organisation.files['logo.jpg'] = BytesIO(b'File content')
    result = ExportSchemaV1().dump(organisation)
    assert result['code'] == 'org'
    assert len(result['files']) == 1
    assert result['files'][0]['key'] == 'logo.jpg'
    assert result['files'][0].get('uri')
