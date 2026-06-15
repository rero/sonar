# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
