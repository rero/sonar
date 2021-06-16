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

"""Test subdivisions facets in users."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_list(app, db, client, deposit, superuser, subdivision):
    """Test subdivision facet."""
    superuser['subdivision'] = {
        '$ref':
        'https://sonar.ch/api/subdivisions/{pid}'.format(
            pid=subdivision['pid'])
    }
    superuser.commit()
    db.session.commit()
    superuser.reindex()

    login_user_via_session(client, email=superuser['email'])
    res = client.get(url_for('invenio_records_rest.user_list'))
    assert res.status_code == 200
    assert res.json['aggregations']['subdivision']['buckets'] == [{
        'key':
        '2',
        'doc_count':
        1,
        'name':
        'Subdivision name'
    }]
