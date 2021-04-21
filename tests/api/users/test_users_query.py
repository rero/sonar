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

"""Test users queries."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_queries(client, superuser, make_user):
    """Test the query user list filtering."""
    login_user_via_session(client, email=superuser['email'])

    headers = [('Content-Type', 'application/json')]

    # No user found
    response = client.get(url_for('invenio_records_rest.user_list',
                                  missing_organisation='1'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 0

    # 1 user found
    make_user('user', None)
    response = client.get(url_for('invenio_records_rest.user_list',
                                  missing_organisation='1'),
                          headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total']['value'] == 1
