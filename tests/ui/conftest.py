# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures and plugins for the UI application."""

import os

import pytest
from invenio_app.factory import create_ui


@pytest.fixture(scope="module")
def harvested_record():
    """Return test XML record."""
    with open(os.path.join(os.path.dirname(__file__), "data", "harvested_record.xml")) as file:
        yield file.read()


@pytest.fixture(scope="module")
def create_app():
    """Create test app."""
    return create_ui
