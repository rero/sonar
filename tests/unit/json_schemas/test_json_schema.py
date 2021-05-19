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

"""Test JSON schema."""

import pytest

from sonar.json_schemas.json_schema_base import JSONSchemaBase


def test_load(app, monkeypatch):
    """Test load."""
    # Non existing schema
    with pytest.raises(Exception) as exception:
        schema = JSONSchemaBase('fakes')
        assert str(
            exception.value) == 'Schema "fakes/fake-v1.0.0.json" not found'

    # Standard schema
    schema = JSONSchemaBase('documents')
    assert schema.get_schema()['title'] == 'Document'

    # Schema for custom resource
    monkeypatch.setattr(
        'sonar.json_schemas.json_schema_base.current_organisation',
        {'code': 'hepvs'})
    monkeypatch.setattr(
        'sonar.json_schemas.json_schema_base.has_custom_resource', lambda *
        args, **kwargs: True)
    schema = JSONSchemaBase('projects')
    assert schema.get_schema()['title'] == 'Research project'
