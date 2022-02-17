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

"""Test extension before request."""

from flask import request, url_for
from invenio_accounts.testutils import login_user_via_session


def test_ext_before_request(client, superuser):
    """Test before request hook in extension."""
    login_user_via_session(client, email=superuser['email'])

    res = client.get(url_for('projects.search'))
    assert res.status_code == 200
    assert request.accept_mimetypes.find('text/csv') == -1

    res = client.get(url_for('projects.search', format='text/csv'))
    assert res.status_code == 200
    assert request.accept_mimetypes.find('text/csv') == 0
