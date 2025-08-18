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

"""Test HEG schema factory."""

import pytest

from sonar.heg.serializers.schemas.factory import SchemaFactory
from sonar.heg.serializers.schemas.medline import MedlineSchema


def test_loader_schema_factory():
    """Test loader schema factory."""
    schema = SchemaFactory.create("Medline")
    assert isinstance(schema, MedlineSchema)

    with pytest.raises(Exception) as exception:
        schema = SchemaFactory.create("not-existing")
        assert str(exception) == 'No schema defined for key "not-existing"'
