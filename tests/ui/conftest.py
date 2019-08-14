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

"""Pytest fixtures and plugins for the UI application."""

from __future__ import absolute_import, print_function

import pytest
from invenio_app.factory import create_ui


@pytest.fixture(scope='module')
def create_app():
    """Create test app."""
    return create_ui


@pytest.fixture(scope='module')
def user_fixture(app):
    """Create user in database."""
    with app.app_context():
        datastore = app.extensions['security'].datastore
        datastore.create_user(email='john.doe@test.com',
                              password='123456',
                              active=True)
        datastore.commit()
    return app
