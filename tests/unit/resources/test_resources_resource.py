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

"""Test resources configuration."""

from flask_security import url_for_security
from invenio_accounts.testutils import login_user_via_view

from sonar.dedicated.hepvs.projects.resource import \
    RecordResourceConfig as HEPVSRecordResourceConfig
from sonar.resources.projects.resource import RecordResourceConfig


def test_config(app, client, make_user, admin):
    """Test resources configuration."""
    user = make_user('admin', 'hepvs')

    # Not logged
    assert isinstance(app.extensions['sonar'].resources['projects'].config(),
                      RecordResourceConfig)

    # Logged as user not belonging to HEPVS.
    login_user_via_view(client, email=admin['email'], password='123456')
    assert isinstance(app.extensions['sonar'].resources['projects'].config(),
                      RecordResourceConfig)

    client.get(url_for_security('logout'))

    # Logged as user from HEPVS.
    login_user_via_view(client, email=user['email'], password='123456')

    # OK, custom config
    assert isinstance(app.extensions['sonar'].resources['projects'].config(),
                      HEPVSRecordResourceConfig)

    # No `resource_name` attribute
    delattr(app.extensions['sonar'].resources['projects'].default_config,
            'resource_name')
    assert isinstance(app.extensions['sonar'].resources['projects'].config(),
                      RecordResourceConfig)
