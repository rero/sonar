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

"""Test collections suggestions."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_suggestions(client, admin, collection, make_collection):
    """Test list collections permissions."""
    make_collection('org')

    login_user_via_session(client, email=admin['email'])

    # 2 results
    res = client.get(url_for('invenio_records_rest.coll_list'))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 2

    # Suggestions does not return the collection corresponding to current PID
    res = client.get(
        url_for('invenio_records_rest.coll_list',
                q='name.value.suggest:Collection name',
                currentPid=collection['pid']))
    assert res.status_code == 200
    assert res.json['hits']['total']['value'] == 1
