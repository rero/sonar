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

"""Test JSON schema factory."""

from sonar.json_schemas.deposits_json_schema import DepositsJSONSchema
from sonar.json_schemas.factory import JSONSchemaFactory
from sonar.json_schemas.json_schema_base import JSONSchemaBase


def test_create(app):
    """Test schema object creation."""
    # No custom schema
    schema = JSONSchemaFactory.create("organisations")
    assert isinstance(schema, JSONSchemaBase)

    # Specific schema
    schema = JSONSchemaFactory.create("deposits")
    assert isinstance(schema, DepositsJSONSchema)
