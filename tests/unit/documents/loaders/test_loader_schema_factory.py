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

"""Test BORIS record loader."""

import pytest

from sonar.modules.documents.loaders.schemas.factory import LoaderSchemaFactory
from sonar.modules.documents.loaders.schemas.rerodoc import RerodocSchema


def test_loader_schema_factory():
    """Test loader schema factory."""
    schema = LoaderSchemaFactory.create('rerodoc')
    assert isinstance(schema, RerodocSchema)

    with pytest.raises(Exception) as exception:
        schema = LoaderSchemaFactory.create('not-existing')
        assert str(exception) == 'No schema defined for key "not-existing"'
