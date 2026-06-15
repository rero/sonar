# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test SONAR proxy."""

from sonar.proxies import sonar
from sonar.resources.projects.service import RecordService


def test_get_endpoints(app):
    """Test list endpoints."""
    endpoints = sonar.endpoints
    assert endpoints["doc"] == "documents"
    assert endpoints["depo"] == "deposits"
    assert endpoints["org"] == "organisations"
    assert endpoints["user"] == "users"
    assert endpoints["projects"] == "projects"


def test_service(app):
    """Test service."""
    service = sonar.service("projects")
    assert isinstance(service, RecordService)

    assert not sonar.service("unknown")
