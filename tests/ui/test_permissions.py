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

"""Test SONAR permissions."""

from flask import url_for
from flask_principal import ActionNeed
from invenio_access.models import ActionUsers

from sonar.modules.permissions import has_admin_access


def test_has_admin_access(app, db, user_fixture):
    """Test error page"""
    datastore = app.extensions['security'].datastore
    user = datastore.find_user(email='john.doe@test.com')

    file_url = url_for('admin.index')
    with app.test_client() as client:
        if user:
            # Login as user
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['_fresh'] = True

            db.session.add(
                ActionUsers.allow(ActionNeed('admin-access'), user=user))
            db.session.commit()

            res = client.get(file_url)
            assert res.status_code == 200
