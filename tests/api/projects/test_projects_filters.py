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

"""Test projects filters."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_filters(client, superuser, project, make_project):
    """Test projects filters."""
    make_project('submitter', 'org')

    login_user_via_session(client, email=superuser['email'])

    # Without filter
    res = client.get(url_for('projects.projects_list'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 2
    assert len(res.json['aggregations']['user']['buckets']) == 2

    # Existing user filter
    res = client.get(
        url_for('projects.projects_list', user='orgadmin'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1
    assert len(res.json['aggregations']['user']['buckets']) == 1

    # Non existing organisation filter
    res = client.get(url_for('projects.projects_list', user='unknown'))
    assert res.status_code == 200
    assert res.json['hits']['total'] == 0
    assert not res.json['aggregations']['user']['buckets']
