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
