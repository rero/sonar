# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures and plugins for the UI application."""

import pytest


@pytest.fixture(scope="module")
def valid_attributes():
    """Fixture for valid attributes return by shibboleth."""
    return {
        "id": ["1"],
        "email": ["john.doe@test.com"],
        "name": ["John Doe"],
    }


@pytest.fixture(scope="module")
def valid_sp_configuration():
    """Fixture for valid service provider configuration."""
    return {
        "strict": True,
        "debug": True,
        "entity_id": "entity_id",
        "x509cert": "./docker/nginx/sp.pem",
        "private_key": "./docker/nginx/sp.key",
    }
