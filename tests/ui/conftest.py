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

"""Pytest fixtures and plugins for the UI application."""

import os

import pytest
from invenio_app.factory import create_ui


@pytest.fixture(scope="module")
def harvested_record():
    """Return test XML output file path."""
    with open(os.path.join(os.path.dirname(__file__), "data", "harvested_record.xml")) as file:
        yield file.read()


@pytest.fixture(scope="module")
def create_app():
    """Create test app."""
    return create_ui
