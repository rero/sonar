# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test loader schema factory."""

import pytest

from sonar.modules.documents.loaders.schemas.archive_ouverte_unige import ArchiveOuverteUnigeSchema
from sonar.modules.documents.loaders.schemas.factory import LoaderSchemaFactory


def test_loader_schema_factory():
    """Test loader schema factory."""
    schema = LoaderSchemaFactory.create("archive_ouverte_unige")
    assert isinstance(schema, ArchiveOuverteUnigeSchema)

    with pytest.raises(Exception) as exception:
        LoaderSchemaFactory.create("not-existing")
    assert str(exception.value) == 'No schema defined for key "not-existing"'
